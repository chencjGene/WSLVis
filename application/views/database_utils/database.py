import numpy as np
import os
from abc import abstractmethod


from ..utils.config_utils import config
from ..utils.helper_utils import pickle_load_data, pickle_save_data, check_dir
from ..utils.helper_utils import json_load_data, json_save_data
from ..utils.log_utils import logger 

class DataBase(object):
    def __init__(self, dataname, suffix="step0"):
        self.dataname = dataname
        self.data_dir = os.path.join(config.data_root, dataname, suffix)
        check_dir(self.data_dir)
        self.raw_data_dir = os.path.join(config.raw_data_root, dataname)
        self.all_data = {}
        self.suffix = suffix

        self.class_name = []
        self.class_name_encoding = {}
        self.X = [] # contains image level features and patch level features
        self.annos  = [] # contains text, image level labels, boundingboxes and their categories
        self.detection = [] # contains detection results
        self.ids = []

        self.train_idx = []
        self.val_idx = []
        self.test_idx = []
        self.redundant_idx = []
        # additional information can be store here
        self.add_info = {}

    @abstractmethod
    def preprocessing_data(self):
        logger.warn("this function should be overrided and"
            "you should nont see this message.")
    
    def save_cache(self,save_method=pickle_save_data):
        """
        this function save all data (variables in self.all_data) in "RawData/all_data.pkl"
        !!!this function should not be overrided
        :return:
        """
        logger.warn("begin saving unprocessed cache of {}".format(self.dataname))
        all_data_name = os.path.join(self.raw_data_dir, config.all_data_cache_name.format(self.suffix))
        save_method(all_data_name, self.all_data)
        logger.info("cache saving done!")

    def load_cache(self, loading_from_buffer=False, load_method=pickle_load_data):
        all_data_name = os.path.join(self.raw_data_dir, config.all_data_cache_name.format(self.suffix))
        if os.path.exists(all_data_name) and loading_from_buffer:
            logger.warn("all data cache exists. load data from cache ... ...".format(all_data_name))
            self.all_data = load_method(all_data_name)
            logger.info("cache loading done!")
            return True
        logger.info("all data cache does not exists.")

    @abstractmethod
    def process_data(self):
        logger.warn("this function should be overrided and "
                    "you should not see this message.")

    def save_processed_data(self, save_method=pickle_save_data):
        filename = os.path.join(self.data_dir, "processed_data{}{}".format(self.suffix, config.pkl_ext))
        # TODO: add time information and warn users when loading
        logger.warn("save processed data in {}".format(filename))
        mat = {}
        # TODO: class_name
        mat[config.class_name] = self.class_name
        mat[config.X_name] = self.X
        mat[config.annos_name] = self.annos
        mat[config.ids_name] = self.ids
        mat[config.detection_name] = self.detection
        mat[config.train_idx_name] = self.train_idx
        mat[config.valid_idx_name] = self.val_idx
        mat[config.test_idx_name] = self.test_idx
        mat[config.redundant_idx_name] = self.redundant_idx
        mat["image_by_type"] = self.image_by_type
        mat["categories"] = self.categories
        mat["labeled_idx"] = self.labeled_idx
        mat[config.add_info_name] = self.add_info
        save_method(filename, mat)
        logger.info("saved processed data.")

    def load_processed_data(self):
        logger.info("begin loading data from processed data!")
        processed_data_filename = os.path.join(self.data_dir, \
            config.processed_dataname.format(self.suffix))
        processed_data = pickle_load_data(processed_data_filename)
        self.class_name = processed_data[config.class_name]
        self.X = processed_data[config.X_name]
        self.annos = processed_data[config.annos_name]
        self.detections = processed_data[config.detection_name]
        self.ids = processed_data[config.ids_name]
        self.train_idx = processed_data[config.train_idx_name]
        self.val_idx = processed_data[config.valid_idx_name]
        self.test_idx = processed_data[config.test_idx_name]
        self.redundant_idx = processed_data[config.redundant_idx_name]
        self.add_info = processed_data[config.add_info_name]

    def save_processed_database(self):
        None