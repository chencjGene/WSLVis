import numpy as np
import os

from ..database_utils.data import Data
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import *

from .model_helper import *

class MMModel(object):
    def __init__(self, dataname=None):
        self.dataname = dataname
        if dataname is None:
            return 
        self._init()
    
    def _init(self):
        self.data = Data(self.dataname)

    def init(self, dataname):
        self.dataname = dataname
        self._init()
    
    def get_tree(self):
        return self.data.tree


    