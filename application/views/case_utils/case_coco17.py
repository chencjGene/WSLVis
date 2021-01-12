import numpy as np
import os
import json

from .case_base import CaseBase
from ..utils.config_utils import config
from ..utils.helper_utils import pickle_save_data, pickle_load_data

class CaseCOCO17(CaseBase):
    def __init__(self):
        dataname = config.coco17
        super(CaseCOCO17, self).__init__(dataname)
        self.step = self.base_config

    def run(self, k=6, evaluate=True, simplifying=False, step=None, use_buffer=False, use_old = False):
        # TODO:
        return None