import unittest

from application.views.database_utils import Data
from application.views.utils.config_utils import config

class DataTest(unittest.TestCase):

    def test_data_database_get_category_pred_image(self):
        d = Data(config.coco17)
        pred = d.get_category_pred(label_type="labeled", data_type="image")
        self.assertEqual(pred.shape, (5000, 65))
        pred = d.get_category_pred(label_type="unlabeled", data_type="image")
        self.assertEqual(pred.shape, (107297, 65))
        pred = d.get_category_pred(label_type="all", data_type="image")
        self.assertEqual(pred.shape, (112297, 65))


    def test_data_database_get_category_pred(self):
        d = Data(config.coco17)
        pred = d.get_category_pred(label_type="labeled", data_type="text")
        self.assertEqual(pred.shape, (5000, 65))
        pred = d.get_category_pred(label_type="unlabeled", data_type="text")
        self.assertEqual(pred.shape, (107297, 65))
        pred = d.get_category_pred(label_type="all", data_type="text")
        self.assertEqual(pred.shape, (112297, 65))

unittest.main()