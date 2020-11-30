import numpy as np
import os
from abc import abstractmethod


from ..utils.config_utils import config
from ..utils.helper_utils import pickle_load_data, pickle_save_data, check_dir
from ..utils.log_utils import logger 

class DataBase(object):
    def __init__(self, dataname):
        self.dataname = dataname
        self.data_dir = os.path.join(config.data_root, dataname)
        check_dir(self.data_dir)
        self.raw_data_dir = os.path.join(config.raw_data_root, dataname)
        self.all_data = {}

        self.class_name = []
        self.class_name_encoding = {}
        self.X = [] # contains image level features and 
        self.annos  = [] # contains text, image level labels, boundingboxes and their categories

        self.train_idx = []
        self.valid_idx = []
        self.test_idx = []
        self.redundant_idx = []
        # additional information can be store here
        self.add_info = {}

    @abstractmethod
    def preprocessing_data(self):
        logger.warn("this function should be overrided and"
            "you should nont see this message.")
    
    def save_cache(self):
        """
        this function save all data (variables in self.all_data) in "RawData/all_data.pkl"
        !!!this function should not be overrided
        :return:
        """
        logger.warn("begin saving unprocessed cache of {}".format(self.dataname))
        all_data_name = os.path.join(self.raw_data_dir, config.all_data_cache_name)
        pickle_save_data(all_data_name, self.all_data)
        logger.info("cache saving done!")

    def load_cache(self, loading_from_buffer=False):
        all_data_name = os.path.join(self.raw_data_dir, config.all_data_cache_name)
        if os.path.exists(all_data_name) and loading_from_buffer:
            logger.warn("all data cache exists. load data from cache ... ...".format(all_data_name))
            self.all_data = pickle_load_data(all_data_name)
            logger.info("cache loading done!")
            return True
        logger.info("all data cache does not exists.")

    @abstractmethod
    def process_data(self):
        logger.warn("this function should be overrided and "
                    "you should not see this message.")

    def save_processed_data(self):
        filename = os.path.join(self.data_dir, "processed_data" + config.pkl_ext)
        # TODO: add time information and warn users when loading
        logger.warn("save processed data in {}".format(filename))
        mat = {}
        # TODO: class_name
        mat[config.class_name] = self.class_name
        mat[config.X_name] = self.X
        mat[config.anns_name] = self.annos
        mat[config.train_idx_name] = self.train_idx
        mat[config.valid_idx_name] = self.valid_idx
        mat[config.test_idx_name] = self.test_idx
        mat[config.redundant_idx_name] = self.redundant_idx
        mat[config.add_info_name] = self.add_info
        pickle_save_data(filename, mat)
        logger.info("saved processed data.")