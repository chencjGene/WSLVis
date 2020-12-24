import numpy as np
import os
import sys
from time import time 
from tqdm import tqdm

if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET

from .database import DataBase
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data
from ..utils.helper_utils import area
from .utils import encoding_categories, decoding_categories 

# COCO_CLASSES = ('person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
#                 'train', 'truck', 'boat', 'traffic light', 'fire hydrant',
#                 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
#                 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
#                 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
#                 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
#                 'kite', 'baseball bat', 'baseball glove', 'skateboard',
#                 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
#                 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
#                 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
#                 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
#                 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
#                 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
#                 'refrigerator', 'book', 'clock', 'vase', 'scissors',
#                 'teddy bear', 'hair drier', 'toothbrush')

def get_label_map(label_file):
    label_map = {}
    labels = open(label_file, 'r')
    class_names = []
    for idx, line in enumerate(labels):
        ids = line.split(',')
        label_map[int(ids[0])] = int(idx)
        class_names.append(ids[2])
    return label_map, class_names

class DataCOCO17(DataBase):
    def __init__(self):
        dataname = config.coco17
        super(DataCOCO17, self).__init__(dataname)
        self.label_map, self.class_name = get_label_map(os.path.join(self.data_dir, "label_map.txt"))
        

    def preprocessing_data(self):
        logger.info("begin preprocessing_data")
        t0 = time()
        # val detection result
        val_detection_path = os.path.join(self.raw_data_dir, \
            "detections_val.pkl")
        val_detection_result = pickle_load_data(val_detection_path)

        # train detection result
        train_detection_path =  os.path.join(self.raw_data_dir, \
            "detections_train.pkl")
        train_detection_result = pickle_load_data(train_detection_path)

        # val groundtruth
        val_instance = json_load_data(os.path.join(config.raw_data_root, "coco17_raw_data", \
            "annotations", "instances_val2017.json"))
        val_images = val_instance["images"]
        val_annos = val_instance["annotations"]

        # train groundtruth
        train_instance = json_load_data(os.path.join(config.raw_data_root, "coco17_raw_data", \
            "annotations", "instances_train2017.json"))
        train_images = train_instance["images"]
        train_annos = train_instance["annotations"]

        # val text
        val_captions = json_load_data(os.path.join(config.raw_data_root, "coco17_raw_data", \
            "annotations", "captions_val2017.json"))
        val_captions = val_captions["annotations"]
        # train text
        train_captions = json_load_data(os.path.join(config.raw_data_root, "coco17_raw_data", \
            "annotations", "captions_train2017.json"))
        train_captions = train_captions["annotations"]

        self.all_data = {
            "train_detections": train_detection_result,
            "val_detections": val_detection_result,
            "train_images": train_images,
            "val_images": val_images,
            "train_annos": train_annos,
            "val_annos": val_annos,
            "train_captions": train_captions,
            "val_captions": val_captions
        }
        # self.save_cache()
        logger.info("preprocessing time: {}".format(time() - t0))
        # import IPython; IPython.embed(); exit()
        
        # annotation_path = os.path.join(self.raw_data_dir, "VOCdevkit" \
        #     "VOC2007", "Annotations", "%s.xml")

    def process_data(self):
        # self.load_cache(loading_from_buffer=True)
        train_detection = self.all_data["train_detections"]
        val_detection = self.all_data["val_detections"]
        train_images = self.all_data["train_images"]
        val_images = self.all_data["val_images"]
        train_annos = self.all_data["train_annos"]
        val_annos = self.all_data["val_annos"]
        train_captions = self.all_data["train_captions"]
        val_captions = self.all_data["val_captions"]

        train_ids = train_detection["img_id"]
        val_ids = val_detection["img_id"]
        train_detection = train_detection["all_boxes"]
        val_detection = val_detection["all_boxes"]
        train_num = len(train_ids)
        val_num = len(val_ids)
        total_num = train_num + val_num
        self.train_idx = np.array(range(train_num))
        self.val_idx = np.array(range(train_num, train_num + val_num))
        self.ids = train_ids + val_ids
        self.annos = [{"bbox":[], "caption": []} for _ in range(total_num)]
        self.detection = [{"bbox":[]} for _ in range(total_num)]

        img_id_2_idx = {}
        for idx, img_id in enumerate(self.ids):
            img_id_2_idx[img_id] = idx
        
        # processing annos
        logger.info('processing annos') 
        for anno in tqdm(train_annos + val_annos):
            img_id = anno["image_id"]
            idx = img_id_2_idx[img_id]
            if not anno["category_id"] in self.label_map:
                continue
            category_id = self.label_map[anno["category_id"]]
            bbox = anno["bbox"]
            bbox[2] += bbox[0]
            bbox[3] += bbox[1]
            a = area(bbox)
            # if a > 2000: # exclude bounding boxes whose areas are less than 2000 
            self.annos[idx]["bbox"].append(bbox + [1, category_id])
        

        for _idx in tqdm(range(train_num + val_num)):
            anno = self.annos[_idx]
            areas = np.array([area(b[:4]) for b in anno["bbox"]])
            all_cat = np.array([b[-1] for b in anno["bbox"]])
            unique_cat = np.unique(all_cat)
            removed_idx = []
            for cat in unique_cat:
                idx_in_cat = np.array(range(len(all_cat)))[all_cat==cat]
                areas_in_cat = areas[idx_in_cat]
                sorted_idx = areas_in_cat.argsort()
                for i, cat_idx in enumerate(sorted_idx):
                    idx = idx_in_cat[cat_idx]
                    if i == (len(sorted_idx) - 1):
                        break
                    if areas[idx] < 2000:
                        removed_idx.append(idx)
            new_annos = []
            for i in range(len(all_cat)):
                if i not in removed_idx:
                    new_annos.append(anno["bbox"][i])
            self.annos[_idx]["bbox"] = new_annos

            new_all_cat = np.array([b[-1] for b in self.annos[_idx]["bbox"]])
            new_unique_cat = np.unique(new_all_cat)
            assert(len(unique_cat) == len(new_unique_cat))
            # if idx == 51:
            #     import IPython; IPython.embed(); exit()
        # processing caption
        logger.info("processing caption")
        for caption in tqdm(train_captions+val_captions):
            try:
                img_id = caption["image_id"]
                idx = img_id_2_idx[img_id]
                cap = caption["caption"]
                self.annos[idx]["caption"].append(cap)
            except Exception as e:
                logger.info(e)

        # # processing detection
        # logger.info('processing detection')
        # for category in tqdm(range(1, len(self.class_name) + 1)):
        #     for idx in range(train_num):
        #         bboxes = train_detection[category][idx]
        #         for bbox in bboxes:
        #             bbox = bbox.tolist() + [category]
        #             self.detection[idx]["bbox"].append(bbox)

        # for category in tqdm(range(1, len(self.class_name) + 1)):
        #     for idx in range(val_num):
        #         bboxes = val_detection[category][idx]
        #         for bbox in bboxes:
        #             bbox = bbox.tolist() + [category]
        #             self.detection[idx + train_num]["bbox"].append(bbox)

        
        # TODO: for debug
        self.detections = self.annos
        
        self.image_by_type = {}
        self.categories = [[] for i in range(len(self.train_idx) + len(self.val_idx))]
        for idx in self.train_idx:
            det = self.detections[idx]
            category = [d[-1] for d in det["bbox"]]
            self.categories[idx] = category
            cat_str = encoding_categories(category)
            if cat_str not in self.image_by_type:
                self.image_by_type[cat_str] = []
            self.image_by_type[cat_str].append(idx)
        


        # import IPython; IPython.embed(); exit()  

    def export_training_data(self):
        # all files: {info, licenses, images, annotations, categories}
        # BBOX = {segmentation: [[1,2.1,3.1]], area, iscrowd, image_id, bbox, category_id, id}
        # image: {license, file_name, coco_url, height, width, date_captured, flickr_url, id}
        self.load_processed_data()

        self.id_to_category = {}
        for i in self.label_map:
            self.id_to_category[self.label_map[i]] = i

        self.ann_ids = 0

        def _export_images_annos(idxs):
            images = []
            annos = []
            for idx in idxs:
                img_id = self.ids[idx]
                bboxes = self.annos[idx]["bbox"]
                if len(bboxes) == 0:
                    continue
                image = {
                    "license": 1,
                    "file_name": "%012d.jpg" % img_id,
                    "coco_url": "",
                    "height": 1,
                    "width": 1,
                    "date_captured": "2013-11-14 17:02:52",
                    "flickr_url": "http:",
                    "id": img_id 
                }
                images.append(image)
                for box in bboxes:
                    annos.append({
                        "segmentations": [[]],
                        "area": 1,
                        "iscrowd": 0,
                        "bbox":[
                            box[0],
                            box[1],
                            box[2] - box[0],
                            box[3] - box[1]
                        ],
                        "image_id": img_id,
                        "category_id": self.id_to_category[box[5]],
                        "id": self.ann_ids
                    })
                    self.ann_ids += 1
            return images, annos

        # process training
        training_instances = json_load_data(os.path.join(config.raw_data_root,
            "coco17_raw_data", "annotations", "instances_train2017.json"))
        images, annos = _export_images_annos(self.train_idx)
        print("train images:", len(images))
        print("train annos:", len(annos))
        training_instances["images"] = images 
        training_instances["annotations"] = annos
        
        # process val
        val_instances = json_load_data(os.path.join(config.raw_data_root,
            "coco17_raw_data", "annotations", "instances_val2017.json"))
        images, annos = _export_images_annos(self.val_idx)
        print("val images:", len(images))
        print("val annos:", len(annos))
        val_instances["images"] = images
        val_instances["annotations"] = annos
        
        json_save_data(os.path.join(config.raw_data_root, "coco17_raw_data",
            "shrink_instances_train2017.json"), training_instances)
        json_save_data(os.path.join(config.raw_data_root, "coco17_raw_data",
            "shrink_instances_val2017.json"), val_instances)

    def postprocess_data(self):
        '''
        statistic, clustering, etc.
        '''
        self.load_processed_data()

