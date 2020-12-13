import numpy as np
import os 

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data

DEBUG = False

class Data(object):
    def __init__(self, dataname):
        self.dataname = dataname 
        self.data_root = os.path.join(config.data_root, self.dataname)
    
        self.class_name = []
        self.class_name_encoding = {}
        self.X = [] # contains image level features and patch level features
        self.annos  = [] # contains text, image level labels, boundingboxes and their categories
        self.detection = [] # contains detection results
        self.ids = []

        self.train_idx = []
        self.valid_idx = []
        self.test_idx = []
        self.redundant_idx = []
        # additional information can be store here
        self.add_info = {}
        
        self._load_data()

    def _load_data(self):
        logger.info("begin loading data from processed data!")
        processed_data_filename = os.path.join(self.data_root, \
            config.processed_dataname)
        processed_data = pickle_load_data(processed_data_filename)
        self.class_name = processed_data[config.class_name]
        self.X = processed_data[config.X_name]
        self.annos = processed_data[config.annos_name]
        self.detections = processed_data[config.detection_name]
        self.ids = processed_data[config.ids_name]
        self.train_idx = processed_data[config.train_idx_name]
        self.valid_idx = processed_data[config.valid_idx_name]
        self.test_idx = processed_data[config.test_idx_name]
        self.redundant_idx = processed_data[config.redundant_idx_name]
        self.add_info = processed_data[config.add_info_name]

        # load hierarchy
        self.tree = pickle_load_data(os.path.join(self.data_root, "hierarchy.json"))

        logger.info("end loading data from processed data!")
    
    

