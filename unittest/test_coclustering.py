import unittest
import numpy as np
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
from application.views.database_utils.set_helper import CoClustering
from application.views.database_utils.spectral_biclustering import SpectralBiclustering
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data
from application.views.database_utils.utils import decoding_categories, encoding_categories


from sklearn.manifold import TSNE, MDS
from sklearn.decomposition import PCA

class Embedder(object):
    def __init__(self, method_name, *args, **kwargs):
        self.projector = None
        self.method_name = method_name
        if method_name == "tsne":
            self.projector = TSNE(*args, **kwargs)
        elif method_name == "pca":
            self.projector = PCA(*args, **kwargs)
        elif method_name == "mds":
            self.projector = MDS(n_jobs=-1, *args, **kwargs)
        else:
            print("the projection method is not supported now!!")

    def fit(self, X, y):
        t = time()
        self.projector.fit(X, y)
        print("{} fit function time cost: {}".format(self.method_name, time()-t))

    def transform(self, X, y):
        t = time()
        self.projector.transform(X, y)
        print("{} transform function time cost: {}".format(self.method_name, time()-t))

    def fit_transform(self, X, y):
        t = time()
        res = self.projector.fit_transform(X, y)
        print("{} fit_transform function time cost: {}".format(self.method_name, time()-t))
        return res


class CoClusteringTest(unittest.TestCase):
    def test_simplecase(self):
        data = np.zeros((6,8))
        data[:3,:3] = 1
        data[3:, 3:] = 1
        np.random.seed(123)
        idx1 = np.array(range(6))
        np.random.shuffle(idx1)
        idx2 = np.array(range(8))
        np.random.shuffle(idx2)
        data = data[idx1]
        data = data[:, idx2]

        # model = CoClustering()
        # C1, C2 = model.fit(data, 2, 2)
        # R = model.rearrange(data, C1, C2)
        model = SpectralBiclustering(n_clusters=[2,2,], method='log',
                             random_state=0)
        model.fit(data)
        fit_data = data[np.argsort(model.row_labels_)]
        fit_data = fit_data[:, np.argsort(model.column_labels_)]
        a = 1

    def test_checkerboard(self):
        n_clusters = (4, 3)
        data, rows, columns = make_checkerboard(
            shape=(300, 300), n_clusters=n_clusters, noise=10,
            shuffle=False, random_state=0)
        
        rng = np.random.RandomState(0)
        row_idx = rng.permutation(data.shape[0])
        col_idx = rng.permutation(data.shape[1])
        R = data[row_idx][:, col_idx]

        model = SpectralBiclustering(n_clusters=n_clusters, method='log',
                            random_state=0, n_components=20)
        model.fit(R.copy())
        idx1 = np.argsort(model.row_labels_)
        fit_data = R[idx1]
        RR = fit_data[:, np.argsort(model.column_labels_)]
        sns.set(font_scale=0.5)
        sns.heatmap(RR)
        plt.savefig("test/mismatch/checkerboard.jpg")
        plt.close()

        tsne = TSNE(n_components=2,random_state=15)
        coor = tsne.fit_transform(R)
        plt.scatter(coor[:,0], coor[:,1])
        plt.savefig("test/mismatch/checkerboard-tsne.jpg")
        plt.close()

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

    def test_hypothese(self):
        
        mat = pickle_load_data("test/mismatch/network.pkl")
        net = mat["gt"]
        net[0,0] = 0
        # net = net / net.max()
        # R = np.power(net, 0.4)
        R = net.astype(float)

        # data = np.zeros((6,8))
        # data[:3,:3] = 1
        # data[3:, 3:] = 1
        # C1 = [[1,0],[1,0],[1,0],[0,1],[0,1],[0,1]]
        # C1 = np.array(C1)
        # C2 = np.array([[1., 0.],
        #                 [1., 0.],
        #                 [1., 0.],
        #                 [0., 1.],
        #                 [0., 1.],
        #                 [0., 1.],
        #                 [0., 1.],
        #                 [0., 1.]])

        
        # n_clusters = (3, 3)
        # data, rows, columns = make_checkerboard(
        #     shape=(300, 300), n_clusters=n_clusters, noise=1,
        #     shuffle=False, random_state=0)
        U, sigma, V = svds(R, k=2)
        # U[U > 0.5] = 0
        plt.scatter(U[:,0], U[:,1])
        plt.savefig("test/test.jpg")
        
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
        k1, k2 = [5,5]
        # model = CoClustering()
        # C1, C2 = model.fit(R, k1, k2)
        # RR = model.rearrange(R, C1, C2)
        # for k1 in tqdm(range(4, 20)):
        #     for k2 in range(4, 50):
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

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(CoClusteringTest("test_simplecase"))
    
    suite =  unittest.TestLoader().loadTestsFromTestCase(CoClusteringTest)
    unittest.TextTestRunner(verbosity=2).run(suite)