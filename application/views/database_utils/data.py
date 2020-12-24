import numpy as np
import os 

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data
from ..database_utils.utils import decoding_categories, encoding_categories

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
        self.image_by_type = processed_data["image_by_type"]
        self.categories = processed_data["categories"]
        self.add_info = processed_data[config.add_info_name]

        # load hierarchy
        self.tree = json_load_data(os.path.join(self.data_root, "hierarchy.json"))

        logger.info("end loading data from processed data!")

    def get_hypergraph(self):
        tree = self.get_tree()
        
        leaf_node = []
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            if len(node["children"]) == 0:
                leaf_node.append(node)
            visit_node.extend(node["children"])

        # name to id map
        name_2_id = {}
        for idx, name in enumerate(self.class_name):
            name_2_id[name.strip("\n")] = idx
        
        id_to_leaf = {}
        for node in leaf_node:
            node["cat_id"] = name_2_id[node["name"]]
            node["sets"] = []
            id_to_leaf[name_2_id[node["name"]]] = node

        set_list = self.get_set()
        for s in set_list:
            categories = decoding_categories(s)
            for c in categories:
                id_to_leaf[c]["sets"].append(s)
        return tree, set_list

    def get_tree(self):
        return self.tree

    def get_set(self):
        all_types = self.image_by_type.keys()
        types = []
        for t in all_types:
            if len(self.image_by_type[t]) > 50 and len(t) > 0:
                types.append(t)
        return types        

