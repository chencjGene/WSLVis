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

COCO_CLASSES = ('person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
                'train', 'truck', 'boat', 'traffic light', 'fire', 'hydrant',
                'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog',
                'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
                'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
                'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
                'kite', 'baseball bat', 'baseball glove', 'skateboard',
                'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
                'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
                'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
                'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
                'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
                'keyboard', 'cell phone', 'microwave oven', 'toaster', 'sink',
                'refrigerator', 'book', 'clock', 'vase', 'scissors',
                'teddy bear', 'hair drier', 'toothbrush')

class DataCOCO17(DataBase):
    def __init__(self):
        dataname = config.coco17
        super(DataCOCO17, self).__init__(dataname)

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

        self.class_name = COCO_CLASSES
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
            category_id = anno["category_id"]
            bbox = anno["bbox"]
            self.annos[idx]["bbox"].append(bbox + [1, category_id])

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

        # processing detection
        logger.info('processing detection')
        for category in tqdm(range(1, len(self.class_name) + 1)):
            for idx in range(train_num):
                bboxes = train_detection[category][idx]
                for bbox in bboxes:
                    bbox = bbox.tolist() + [category]
                    self.detection[idx]["bbox"].append(bbox)

        for category in tqdm(range(1, len(self.class_name) + 1)):
            for idx in range(val_num):
                bboxes = train_detection[category][idx]
                for bbox in bboxes:
                    bbox = bbox.tolist() + [category]
                    self.detection[idx + train_num]["bbox"].append(bbox)

        import IPython; IPython.embed(); exit()  