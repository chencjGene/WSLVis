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
from application.views.model_utils.ranker import lap_score

from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA

class CoClusteringTest(unittest.TestCase):
    def test_model(self):
        m = WSLModel(dataname=config.coco17, step=1)
        m.run()
        class_name = m.data.class_name[1:]
        row_labels = m.text_labels
        col_labels = m.image_labels
        for i in range(m.config["text_k"]):
            selected = row_labels==i
            # print("total num of selected", sum(selected))
            print(np.array(class_name)[selected])
        a = 1

    def test_rank(self):
        m = WSLModel(dataname=config.coco17, step=1)
        m.run()
        res = m.get_rank(4)
        # image_ids = m.image_ids_of_clusters[4]
        # R = np.zeros((len(image_ids), 65))
        # for idx, img_id in enumerate(image_ids):
        #     res = m.data.get_detection_result(int(img_id))
        #     for det in res:
        #         if det[-2] > m.data.conf_thresh:
        #             R[idx, det[-1]] = 1
        # R = R / (R.sum(axis=1).reshape(-1, 1) + 1e-12)
        # s = lap_score(R.T)
        a = 1