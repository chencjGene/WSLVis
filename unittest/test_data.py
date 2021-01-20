import unittest

from application.views.database_utils import Data
from application.views.database_utils.utils import multiclass_precision_and_recall
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
        gt = d.get_groundtruth_labels(label_type="labeled")
        precision, recall = multiclass_precision_and_recall(gt, pred)
        self.assertAlmostEqual(precision[33], 0.638, delta=0.001)
        self.assertAlmostEqual(recall[33], 0.302, delta=0.001)
        pred = d.get_category_pred(label_type="unlabeled", data_type="text")
        self.assertEqual(pred.shape, (107297, 65))
        pred = d.get_category_pred(label_type="all", data_type="text")
        self.assertEqual(pred.shape, (112297, 65))

    def test_data_database_get_category_pred_step1(self):
        d = Data(config.coco17, suffix="step1")
        pred = d.get_category_pred(label_type="labeled", data_type="text")
        self.assertEqual(pred.shape, (5000, 65))
        gt = d.get_groundtruth_labels(label_type="labeled")
        precision, recall = multiclass_precision_and_recall(gt, pred)
        print(precision[33], recall[33])
        self.assertAlmostEqual(precision[33], 0.850, delta=0.001)
        self.assertAlmostEqual(recall[33], 0.971, delta=0.001)


    def test_data_database_get_set(self):
        d = Data(config.coco17)
        d.get_set()

    
    def test_get_image_by_type(self):
        d = Data(config.coco17, suffix="step1")
        a = 1

if __name__ == "__main__":
    suite = unittest.TestSuite()
    # suite.addTest(DataTest(""))
    
    suite =  unittest.TestLoader().loadTestsFromTestCase(DataTest)
    unittest.TextTestRunner(verbosity=2).run(suite)