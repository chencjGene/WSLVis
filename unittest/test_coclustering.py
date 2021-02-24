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

from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA

def load_R(class_name, kmeans):
    R_path = "test/feature/cluster_R.npy"
    R = np.zeros((len(class_name), len(np.unique(kmeans))))
    if os.path.exists(R_path):
        R = np.load(R_path)
    else:
        print("R.shape", R.shape)
        for i in range(100):
            r = R[:,i]
            idxs = np.array(range(len(kmeans)))[kmeans == i]
            for j in idxs:
                res = d.set_helper.get_detection_result(int(j))
                # res = d.set_helper.get_anno_bbox_result(int(j))
                for det in res:
                    if det[-2] > 0.5:
                        r[det[-1]] += 1
            R[:, i] = r
        np.save("test/feature/cluster_R.npy", R)
    return R


class CoClusteringTest(unittest.TestCase):

    def test_cv(self):
        kmeans = np.load("test/feature/kmeans-3.npy")
        d = Data(config.coco17, step=1)

        class_name = d.class_name
        R = load_R(class_name, kmeans)
        text_feature = np.load("test/word_embedding/word_feature.npy")
        text_feature = text_feature[1:]
        
        # normalization
        R = R[1:, :]
        class_name = class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.41)


        k1_range = list(range(2,20))
        k2_range = list(range(2,20))
        v = []
        for k1 in k1_range:
            for k2 in k2_range:
                try:
                    clf = CoClustering(k1, k2, 0, verbose=0)
                    C1, C2 = clf.fit(R)
                    norm_C1 = C1 / C1.sum(axis=0)
                    norm_C2 = C2 / C2.sum(axis=0)
                    S = norm_C1.T.dot(R).dot(norm_C2)
                    c = CoefficientVariance(S)
                    # pair.append([k2, c])
                    v.append(c)
                    print("k1: {}, k2: {}, c: {}".format(k1, k2, c))
                except:
                    import IPython; IPython.embed(); exit()
        # for k2, c in pair:
        #     print("k2: {}, c: {}".format(k2, c))
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        xpos, ypos = np.meshgrid(k1_range, k2_range, indexing="ij")
        xpos = xpos.ravel()
        ypos = ypos.ravel()
        dx = dy = 0.3 * np.ones_like(0)
        dz = np.array(v)
        print("result:", np.round(dz, 3))
        ax.bar3d(xpos, ypos, 0, dx, dy, dz, zsort="average")
        plt.savefig("test/mismatch/3d.jpg")
        plt.close()
        exit()

    def test_view_point(self):
        k1_range = list(range(2,15))
        k2_range = list(range(2,20))
        xpos, ypos, dx, dy, dz = pickle_load_data("test/mismatch/3d_real_data.pkl")
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.bar3d(xpos, ypos, 0, dx, dy, dz, zsort="average")
        # ax.view_init(elev=10, azim=190)
        plt.savefig("test/mismatch/3d.jpg")
        plt.show()
        plt.close()
        dz = dz.reshape(5,5)
        gradient = calculate_gradient(dz)
        res = find_turning_points(gradient)
        a = 1 


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

    def test_spectral_clustering_by_clusters(self):
        kmeans = np.load("test/feature/kmeans-3.npy")
        d = Data(config.coco17, suffix="step1")
        image_labels = d.get_category_pred(label_type="all", data_type="image")
        text_labels = d.get_category_pred(label_type="all", data_type="text")
        single_mismatch = (image_labels!=text_labels).sum(axis=1)
        cluster_mismatch = []
        for i in range(100):
            idxs = np.array(range(len(kmeans)))[kmeans == i]
            cluster_mismatch.append(single_mismatch[idxs].sum())
        cluster_mismatch = np.array(cluster_mismatch)
        # sets = d.get_set()
        # image_by_type, sets = d.set_helper.get_real_set()
        class_name = d.class_name
        R = load_R(class_name, kmeans)

        # normalization
        R = R[1:, :]
        class_name = class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.4)

        # coclustering 
        k1, k2 = [12, 12]
        model = SpectralBiclustering(n_clusters=[k1, k2], method='bistochastic',
                            random_state=0, n_components=14)
        model.fit(R.copy())
        idx1 = np.argsort(model.row_labels_)
        fit_data = R[idx1]
        RR = fit_data[:, np.argsort(model.column_labels_)]
        
        for i in range(k1):
            selected = model.row_labels_==i
            # print("total num of selected", sum(selected))
            print(np.array(class_name)[selected])
        
        # for i in range(k2):
        #     selected = model.column_labels_ == i
        #     # print("{}: total num of selected {}".format(i, sum(selected)))
        #     # print(np.array(range(100))[selected])
        #     print(cluster_mismatch[selected], "**", cluster_mismatch[selected].sum())


        # visualization 
        sns.set(font_scale=0.5)
        sns.heatmap(RR, yticklabels=np.array(class_name)[idx1])
        plt.savefig("test/feature/cluster_R.jpg")
        plt.close()

        a = 1


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(CoClusteringTest("test_cv"))
    
    # # test all cases
    # suite =  unittest.TestLoader().loadTestsFromTestCase(CoClusteringTest)
    unittest.TextTestRunner(verbosity=2).run(suite)