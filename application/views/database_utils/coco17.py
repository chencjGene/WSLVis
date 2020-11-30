import numpy as np
import os
import sys
from time import time 

if sys.version_info[0] == 2:
    import xml.etree.cElementTree as ET
else:
    import xml.etree.ElementTree as ET

from .database import DataBase
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data

VOC_CLASSES = (  # always index 0
    'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse',
    'motorbike', 'person', 'pottedplant',
    'sheep', 'sofa', 'train', 'tvmonitor')

class DataCOCO17(DataBase):
    def __init__(self):
        dataname = config.coco17
        super(DataCOCO17, self).__init__(dataname)

    def preprocessing_data(self):
        print("begin preprocessing_data")
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

        import IPython; IPython.embed(); exit()