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
from ..utils.helper_utils import pickle_load_data, pickle_save_data

VOC_CLASSES = (  # always index 0
    'aeroplane', 'bicycle', 'bird', 'boat',
    'bottle', 'bus', 'car', 'cat', 'chair',
    'cow', 'diningtable', 'dog', 'horse',
    'motorbike', 'person', 'pottedplant',
    'sheep', 'sofa', 'train', 'tvmonitor')

class DataVOC07(DataBase):
    def __init__(self):
        dataname = config.voc07
        super(DataVOC07, self).__init__(dataname)

    def preprocessing_data(self):
        print("begin preprocessing_data")
        t0 = time()
        # detection result
        detection_path = os.path.join(self.raw_data_dir, \
            self.dataname, "detections.pkl")
        detection_result = pickle_load_data(detection_path)

        # # groundtruth
        # img_ids = []
        # for line in open(os.path.join(self.raw_data_dir, "VOCdevkit", "VOC2007", \
        #     "ImageSets", "Main", "test.txt")): # TODO: change for training data
        #     img_ids.append(line.strip())
        
        # annotation_path = os.path.join(self.raw_data_dir, "VOCdevkit" \
        #     "VOC2007", "Annotations", "%s.xml")
        
