import numpy as np
import os
import json

from .case_base import CaseBase
from ..utils.config_utils import config
from ..utils.helper_utils import pickle_save_data, pickle_load_data
from ..utils.log_utils import logger

class CaseCOCO17(CaseBase):
    def __init__(self, case_mode):
        dataname = config.coco17
        super(CaseCOCO17, self).__init__(dataname, case_mode)
        self.step = self.base_config

    def run(self, use_buffer=False):
        # if step and self.case_mode:
        #     raise ValueError("case_mode is set but step is provided")

        if self.step == 0:
            None
        elif self.step == 1:
            if use_buffer and self.model.buffer_exist():
                None # TODO:
                return 

        self.model.run()

        return None