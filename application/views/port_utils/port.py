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
    
    def _init(self, step):
        # self.data = Data(self.dataname)
        # self.model = WSLModel(self.dataname) # init
        self.case_util = get_case_util(self.dataname, self.case_mode)
        self.case_util.set_step(step)
        # self.case_util.connect_model(self.model) 
        self.model = self.case_util.create_model(WSLModel)


    def reset(self, dataname, step=None):
        self.dataname = dataname
        self._init(step)

    def run_model(self):
        self.model = self.case_util.run(use_buffer=False)

    def get_current_hypergraph(self):
        return self.model.get_current_hypergraph()

    def get_rank(self, image_cluster_ids):
        if len(image_cluster_ids) == 0:
            image_cluster_ids = list(range(len(self.model.image_cluster_list)))
        res = {}
        for cluster_id in image_cluster_ids:
            res[cluster_id] = self.model.get_rank(cluster_id)
        return res

    def get_manifest(self):
        res = self.case_util.get_base_config()
        res["real_step"] = self.model.step
        res["class_name"] = self.model.data.class_name
        res["label_consistency"] = res["parameters"][str(self.case_util.step)]["label_consistency"]
        res["symmetrical_consistency"] = res["parameters"][str(self.case_util.step)]["symmetrical_consistency"]
        del res["parameters"]
        return res