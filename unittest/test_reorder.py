import unittest
import numpy as np
import os
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from tqdm import tqdm
from time import time
from sklearn.cluster import SpectralBiclustering

from sklearn.datasets import make_checkerboard
from sklearn.cluster import SpectralBiclustering
from sklearn.metrics import consensus_score
from sklearn.utils.extmath import (make_nonnegative, randomized_svd,
                             safe_sparse_dot)

from scipy.sparse.linalg import eigsh, svds

from application.views.database_utils import Data
from application.views.model_utils import CoClustering, DTPP, CoefficientVariance
from application.views.model_utils import calculate_gradient, find_turning_points
# from application.views.database_utils.set_helper import CoClustering, DTPP
from application.views.database_utils.spectral_biclustering import SpectralBiclustering
from application.views.database_utils.spectral_biclustering import \
    _log_normalize, _bistochastic_normalize, _scale_normalize
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data, pickle_save_data
from application.views.database_utils.utils import decoding_categories, encoding_categories
from application.views.model_utils import WSLModel
from application.views.model_utils.coclustering import reordering

from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA



class CoClusteringTest(unittest.TestCase):
    def test_reorder(self):
        data = np.zeros((5, 6))
        data[:3, :3] = 1
        data[3:, 3:] = 1

        np.random.seed(123)
        idx = np.array(range(5))
        np.random.shuffle(idx)
        data = data[idx, :]
        idx = np.array(range(6))
        np.random.shuffle(idx)
        data = data[:, idx]

        row_order, column_order = reordering(data)
        a = data[row_order, :]
        a = a[:, column_order]

        a = 1

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(CoClusteringTest("test_reorder"))
    
    # # test all cases
    # suite =  unittest.TestLoader().loadTestsFromTestCase(CoClusteringTest)
    unittest.TextTestRunner(verbosity=2).run(suite)