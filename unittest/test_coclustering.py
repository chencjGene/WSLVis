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
from application.views.database_utils.set_helper import CoClustering, DTPP
from application.views.database_utils.spectral_biclustering import SpectralBiclustering
from application.views.database_utils.spectral_biclustering import \
    _log_normalize, _bistochastic_normalize, _scale_normalize
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data
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

    def test_checkerboard(self):
        n_clusters = (4, 3)
        data, rows, columns = make_checkerboard(
            shape=(300, 300), n_clusters=n_clusters, noise=10,
            shuffle=False, random_state=0)
        
        rng = np.random.RandomState(0)
        row_idx = rng.permutation(data.shape[0])
        col_idx = rng.permutation(data.shape[1])
        R = data[row_idx][:, col_idx]

        k1, k2 = n_clusters
        # k1, k2 = [3,4]
        # R = R.T
        
        clf = CoClustering(k1, k2, 0, 20)
        C1, C2 = clf.fit(R)
        row_labels = np.dot(C1, np.array(range(k1)).reshape(-1,1)).reshape(-1)
        col_labels = np.dot(C2, np.array(range(k2)).reshape(-1,1)).reshape(-1)

        # model = SpectralBiclustering(n_clusters=n_clusters, method='log',
        #                     random_state=0, n_components=20)
        # model.fit(R.copy())
        # row_labels = model.row_labels_
        # col_labels = model.column_labels_

        idx1 = np.argsort(row_labels)
        fit_data = R[idx1]
        RR = fit_data[:, np.argsort(col_labels)]
        sns.set(font_scale=0.5)
        sns.heatmap(RR)
        plt.savefig("test/mismatch/checkerboard.jpg")
        plt.close()

        # tsne = TSNE(n_components=2,random_state=15)
        # coor = tsne.fit_transform(R)
        # plt.scatter(coor[:,0], coor[:,1])
        # plt.savefig("test/mismatch/checkerboard-tsne.jpg")
        # plt.close()

        a = 1

    def test_imagedata(self):
        d = Data(config.coco17, suffix="step1")
        image_by_type, sets = d.set_helper.get_real_image()
        class_name = d.class_name
        R = []
        for i in range(len(sets)):
            set_name = sets[i]
            cats = decoding_categories(sets[i])
            image_len = len(image_by_type[set_name])
            for j in range(image_len):
                v = np.zeros(len(class_name))
                v[cats] = 1
                R.append(v)
        R = np.array(R).T
        k1, k2 = [9, 15]
        model = SpectralBiclustering(n_clusters=[k1, k2], method='log', \
                            random_state=0, n_components=20)
        model.fit(R.copy())
        idx1 = np.argsort(model.row_labels_)
        fit_data = R[idx1]
        RR = fit_data[:, np.argsort(model.column_labels_)]

        for i in range(k1):
            selected = model.row_labels_==i
            print("total num of selected", sum(selected))
            print(np.array(class_name)[selected])
            a = model.X_pw_dis[selected]
            a = a[:, selected]
            a = 1
        
        # plt.figure(figsize=(6, 6))
        # plt.matshow(R, cmap=plt.cm.Blues, fignum=0)
        # plt.savefig("test/mismatch/image_rawdata.jpg")
        # plt.close()

        a = 1

    def test_label_label(self):
        d = Data(config.coco17, suffix="step1")
        image_by_type, sets = d.set_helper.get_real_set()
        mat = pickle_load_data("test/mismatch/network.pkl")
        net = mat["gt"]
        net[0,0] = 0
        net[4, 64] = net[64, 4] = 0
        net[13, 64] = net[64, 13] = 0
        net = net / net.max()
        R = np.power(net, 0.4)
        class_name = d.class_name
        k1, k2 = [12, 12]
        
        model = SpectralBiclustering(n_clusters=[k1, k2], method='log',
                            random_state=0, n_components=12)
        model.fit(R.copy())
        idx1 = np.argsort(model.row_labels_)
        fit_data = R[idx1]
        RR = fit_data[:, np.argsort(model.column_labels_)]

        for i in range(k1):
            selected = model.row_labels_==i
            # print("total num of selected", sum(selected))
            print(np.array(class_name)[selected])
        a = 1

    def test_realdata(self):
        d = Data(config.coco17, suffix="step1")
        # sets = d.get_set()
        image_by_type, sets = d.set_helper.get_real_set()
        class_name = d.class_name
        set_num = len(sets)
        class_num = len(class_name)
        R = np.zeros((class_num, set_num))
        for i in range(set_num):
            cats = decoding_categories(sets[i])
            R[cats, i] = len(image_by_type[sets[i]])
        R = R / R.max()
        R = np.power(R, 0.4)
            # R[cats, i] = 1
        print("R shape", R.shape)
        R = R[1:, :]
        class_name = class_name[1:]
        for k1 in [12]:
            for k2 in [15]:
                model = SpectralBiclustering(n_clusters=[k1, k2], method='log',
                                    random_state=0, n_components=50)
                model.fit(R.copy())
                idx1 = np.argsort(model.row_labels_)
                fit_data = R[idx1]
                RR = fit_data[:, np.argsort(model.column_labels_)]

                for i in range(k1):
                    selected = model.row_labels_==i
                    print("total num of selected", sum(selected))
                    print(np.array(class_name)[selected])
                    # a = model.X_pw_dis[selected]
                    # a = a[:, selected]
                    # a = 1

                sorted_name = [class_name[i] for i in idx1]
                # print("C1 cluster size:", C1.sum(axis=0))
                # print("C2 cluster size:", C2.sum(axis=0))
                sns.set(font_scale=0.5)
                sns.heatmap(RR, yticklabels=sorted_name)
                plt.savefig("test/mismatch/coclustering_{}_{}.jpg".format(k1, k2))
                plt.close()
        
        tsne = TSNE(n_components=2,random_state=15, verbose=1)
        coor = tsne.fit_transform(R)
        plt.scatter(coor[:,0], coor[:,1])
        plt.savefig("test/mismatch/coclustering-tsne.jpg")
        plt.close() 
        a = 1

    def test_DTPP(self):
        kmeans = np.load("test/feature/kmeans-3.npy")
        d = Data(config.coco17, suffix="step1")

        class_name = d.class_name
        R = load_R(class_name, kmeans)
        text_feature = np.load("test/word_embedding/word_feature.npy")
        text_feature = text_feature[1:]
        
        # normalization
        R = R[1:, :]
        class_name = class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.4)

        k1, k2 = [12, 12]

        DTPP(R, k1, k2)

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

    def test_coclustering_by_clusters(self):
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

        k1, k2 = [12, 12]
        clf = CoClustering(k1, k2, 0)
        # R = _bistochastic_normalize(R) # normalization
        C1, C2 = clf.fit(R, text_feature)
        row_labels = np.dot(C1, np.array(range(k1)).reshape(-1,1)).reshape(-1)
        col_labels = np.dot(C2, np.array(range(k2)).reshape(-1,1)).reshape(-1)
        for i in range(k1):
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
    suite.addTest(CoClusteringTest("test_simplecase"))
    
    suite =  unittest.TestLoader().loadTestsFromTestCase(CoClusteringTest)
    unittest.TextTestRunner(verbosity=2).run(suite)