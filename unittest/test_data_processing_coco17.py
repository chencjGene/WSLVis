import unittest
import numpy as np
import os 

from application.views.database_utils.coco17 import DataCOCO17
from application.views.database_utils import Data
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config

class COCO17Test(unittest.TestCase):
    
    def test_step0_image_output(self):
        d = DataCOCO17(suffix="step0")
        image_output = np.load(os.path.join(d.raw_data_dir, "train_image_output.npy"))
        self.assertEqual(image_output.sum(), 0)
    