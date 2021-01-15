import numpy as np
import os
import sys
from time import time 
from tqdm import tqdm
import sqlite3

if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET

from .database import DataBase
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data
from ..utils.helper_utils import area, sigmoid
from .utils import encoding_categories, decoding_categories 

def get_label_map(label_file):
    label_map = {}
    labels = open(label_file, 'r')
    class_names = []
    for idx, line in enumerate(labels):
        ids = line.split(',')
        label_map[int(ids[0])] = int(idx)
        class_names.append(ids[2].strip("\n"))
    return label_map, class_names

def process_extracted_result(result):
    map = {}
    for d in tqdm(result):
        image_id = d["image_id"][0].decode()
        logits = d["logits"][0].tolist()
        label = d["label"][0].tolist()
        output_t = sigmoid(d["output_t"][0])
        string = [t.decode() for t in d["string"][0]]
        activations = []
        for idx, text in enumerate(string):
            pred = output_t[idx] > 0.5
            cats = np.nonzero(pred)
            probs = output_t[idx][cats]
            if len(cats[0]) > 0:
                activations.append({
                    "idx": idx,
                    "text": text,
                    "cats": cats[0].tolist(),
                    "probs": probs.tolist()
                })
        map[image_id] = {
            "logits": logits,
            "label": label,
            "activations": activations,
            "string": string,
        }
    return map

def jsonify(detection_result):
    for i in range(66):
        cat_res = detection_result["all_boxes"][i]
        for idx, boxs in enumerate(cat_res):
            if type(boxs) == np.ndarray:
                cat_res[idx] = boxs.tolist()
            # else:
            #     import IPython; IPython.embed(); exit()
    return detection_result

class DataCOCO17(DataBase):
    def __init__(self, suffix=""):
        dataname = config.coco17
        super(DataCOCO17, self).__init__(dataname, suffix)
        self.label_map, self.class_name = get_label_map(os.path.join(\
            self.data_all_step_dir, "label_map.txt"))
        
    def preprocessing_data(self):
        logger.info("begin preprocessing_data")
        t0 = time()
    
        logger.info("loading detection results")
        # val detection result
        val_detection_path = os.path.join(self.raw_data_dir, \
            "detections_val.pkl")
        val_detection_result = pickle_load_data(val_detection_path)
        val_detection_result = jsonify(val_detection_result)

        # import IPython; IPython.embed(); exit()

        # train detection result
        train_detection_path =  os.path.join(self.raw_data_dir, \
            "detections_train.pkl")
        train_detection_result = pickle_load_data(train_detection_path)
        train_detection_result = jsonify(train_detection_result)

        logger.info("loading groundtruth")
        # val groundtruth
        val_instance = json_load_data(os.path.join(self.raw_data_all_step_dir, \
            "shrink_instances_val2017.json"))
        val_images = val_instance["images"]
        val_annos = val_instance["annotations"]

        # train groundtruth
        train_instance = json_load_data(os.path.join(self.raw_data_all_step_dir, \
            "shrink_instances_train2017.json"))
        train_images = train_instance["images"]
        train_annos = train_instance["annotations"]

        # train id in order
        train_ids = open(os.path.join(self.raw_data_all_step_dir, \
            "shrink_train2017_random_list.txt"), "r").read().strip("\n").split("\n")

        logger.info("loading captions")
        # val text
        val_captions = json_load_data(os.path.join(self.raw_data_all_step_dir, \
            "captions_val2017.json"))
        val_captions = val_captions["annotations"]
        # train text
        train_captions = json_load_data(os.path.join(self.raw_data_all_step_dir, \
            "captions_train2017.json"))
        train_captions = train_captions["annotations"]

        logger.info("processing extracted labels")
        # train extracted labels
        train_extracted_labels = pickle_load_data(os.path.join(self.raw_data_dir, \
            "train_result_text.pkl"))
        train_extracted_labels = process_extracted_result(train_extracted_labels)

        # val extracted labels
        val_extracted_labels = pickle_load_data(os.path.join(self.raw_data_dir,
            "val_result_text.pkl"))
        val_extracted_labels = process_extracted_result(val_extracted_labels)

        train_image_output = np.load(os.path.join(self.raw_data_dir,
            "train_image_output.npy")).tolist()
        val_image_output = np.load(os.path.join(self.raw_data_dir,
            "val_image_output.npy")).tolist()

        self.all_data = {
            "train_detections": train_detection_result,
            "val_detections": val_detection_result,
            "train_images": train_images,
            "val_images": val_images,
            "train_annos": train_annos,
            "val_annos": val_annos,
            "train_captions": train_captions,
            "val_captions": val_captions,
            "train_extracted_labels": train_extracted_labels,
            "val_extracted_labels": val_extracted_labels,
            "train_ids": train_ids,
            "train_image_output": train_image_output,
            "val_image_output": val_image_output,
        }
        # import IPython; IPython.embed(); exit()
        self.save_cache(save_method=json_save_data)
        logger.info("preprocessing time: {}".format(time() - t0))
    
    def process_data(self):
        self.load_cache(loading_from_buffer=True, load_method=json_load_data)
        train_detection = self.all_data["train_detections"]
        val_detection = self.all_data["val_detections"] # disable detection result for debug
        train_images = self.all_data["train_images"]
        val_images = self.all_data["val_images"]
        train_annos = self.all_data["train_annos"]
        val_annos = self.all_data["val_annos"]
        train_captions = self.all_data["train_captions"]
        val_captions = self.all_data["val_captions"]
        train_extracted_labels = self.all_data["train_extracted_labels"]
        val_extracted_labels = self.all_data["val_extracted_labels"]
        train_ids = self.all_data["train_ids"]
        train_image_output = self.all_data["train_image_output"]
        val_image_output = self.all_data["val_image_output"]


        # train_ids = train_detection["img_id"]
        # val_ids = val_detection["img_id"]
        train_ids = [int(i) for i in train_ids]
        val_ids = [int(d["id"]) for d in val_images]
        train_detection = train_detection["all_boxes"]
        val_detection = val_detection["all_boxes"]
        train_num = len(train_ids)
        val_num = len(val_ids)
        total_num = train_num + val_num
        self.labeled_idx = np.array(range(5000)) # TODO
        self.train_idx = np.array(range(train_num))
        self.val_idx = np.array(range(train_num, train_num + val_num))
        self.ids = train_ids + val_ids
        self.annos = [{"bbox":[], "caption": []} for _ in range(total_num)]
        self.detection = [{"bbox":[]} for _ in range(total_num)]

        img_id_2_idx = {}
        for idx, img_id in enumerate(self.ids):
            img_id_2_idx[img_id] = idx

        # import IPython; IPython.embed(); exit()

        # processing annos
        logger.info('processing annos')
        exclude = [] 
        for anno in tqdm(train_annos + val_annos):
            img_id = anno["image_id"]
            try:
                idx = img_id_2_idx[img_id]
            except Exception as e:
                # logger.info(e)
                exclude.append(img_id)
            category_id = self.label_map[anno["category_id"]]
            bbox = anno["bbox"]
            bbox[2] += bbox[0]
            bbox[3] += bbox[1]
            a = area(bbox)
            self.annos[idx]["bbox"].append(bbox + [1, category_id])
        logger.info("exclude {}".format(len(exclude)))
        
        # processing caption
        logger.info("processing caption")
        for caption in tqdm(train_captions+val_captions):
            try:
                img_id = caption["image_id"]
                idx = img_id_2_idx[img_id]
                cap = caption["caption"]
                self.annos[idx]["caption"].append(cap)
            except Exception as e:
                # logger.info(e)
                None


        # processing detection
        logger.info('processing detection')
        for category in tqdm(range(1, len(self.class_name) + 1)):
            for idx in range(train_num):
                bboxes = train_detection[category][idx]
                for bbox in bboxes:
                    bbox = bbox + [category]
                    self.detection[idx]["bbox"].append(bbox)
        
        self.image_by_type = {}
        self.categories = [[] for i in range(len(self.train_idx) + len(self.val_idx))]
        for idx in self.train_idx:
            det = self.detection[idx]
            category = [d[-1] for d in det["bbox"]]
            self.categories[idx] = category
            cat_str = encoding_categories(category)
            if cat_str not in self.image_by_type:
                self.image_by_type[cat_str] = []
            self.image_by_type[cat_str].append(int(idx))

        # processing extracted labels
        for i, idx in tqdm(enumerate(self.train_idx)):
            img_id = self.ids[idx]
            extracted_labels = train_extracted_labels[str(img_id)]
            extracted_labels["output_v"] = train_image_output[i]
            self.annos[idx]["extracted_labels"] = extracted_labels
        
        for i, idx in tqdm(enumerate(self.val_idx)):
            img_id = self.ids[idx]
            extracted_labels = val_extracted_labels[str(img_id)]
            extracted_labels["output_v"] = val_image_output[i]
            self.annos[idx]["extracted_labels"] = extracted_labels
            # for act in extracted_labels["activations"]:
            #     image_idx = act["idx"]
            #     text = act["text"]
            #     cats = act["cats"]
            #     probs = act["probs"]
            #     for i, c in enumerate(cats):
            #         if text not in self.extracted_labels_by_cat[c]:
            #             self.extracted_labels_by_cat[c][text] = []
            #         self.extracted_labels_by_cat[c][text].append({
            #             "id": image_idx,
            #             "prob": probs[i]
            #         })

        self.labeled_idx = self.labeled_idx.tolist()
        self.train_idx = self.train_idx.tolist()
        self.val_idx = self.val_idx.tolist()