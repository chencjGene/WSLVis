from .case_base import CaseBase
from .case_coco17 import CaseCOCO17

from ..utils.config_utils import config

def get_case_util(dataname):
    if dataname.lower() == config.coco17.lower():
        return CaseCOCO17()
    else:
        raise ValueError("unsupport dataname {}".format(dataname))