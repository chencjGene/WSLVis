import numpy as np
import os
from ..utils.helper_utils import json_load_data, pickle_load_data
from ..utils.helper_utils import pickle_save_data, json_save_data
from ..utils.config_utils import config

class CaseBase():
    def __init__(self, dataname):
        self.dataname = dataname
        
        self.model = None
        self.base_config = None
        self.step = 0

        self.pred_result = {}

        self._load_base_config()
        
    def connect_data(self, model):
        self.model = model

    def _load_base_config(self):
        json_data = json_load_data(os.path.join(config.case_util_root, "case_config.json"))
        try:
            self.base_config = json_data[self.dataname]
        except:
            self.base_config = {
                "k": 6,
                "step": 0
            }

    def load_data(self, name):
        # TODO:
        return None