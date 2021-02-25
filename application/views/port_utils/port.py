import numpy as np
import os

from ..case_utils import get_case_util
from ..model_utils import WSLModel
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import *

from .port_helper import *

class Port(object):
    def __init__(self, dataname=None, step=None):
        self.dataname = dataname
        self.step = step
        self.case_mode = True
        if dataname is None:
            return 
        self._init()
    
    def _init(self):
        # self.data = Data(self.dataname)
        # self.model = WSLModel(self.dataname) # init
        self.case_util = get_case_util(self.dataname, self.case_mode)
        # self.case_util.connect_model(self.model) 
        self.model = self.case_util.create_model(WSLModel)


    def reset(self, dataname, step=None):
        self.dataname = dataname
        self.step = step
        self._init()

    def run_model(self):
        self.model = self.case_util.run(use_buffer=False)

    def get_current_hypergraph(self):
        return self.model.get_current_hypergraph()

    # def get_tree(self):
    #     return self.data.tree

    # def get_type(self):
    #     return self.data.get_type()
    
    def get_manifest(self):
        return self.case_util.get_base_config()