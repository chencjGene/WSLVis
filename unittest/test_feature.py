import numpy as np
import umap 
import matplotlib.pyplot as plt
import unittest
import pickle
import os 
import seaborn as sns

from sklearn.datasets import load_digits
from sklearn.datasets import fetch_openml
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, MiniBatchKMeans

from application.views.database_utils import Data
from application.views.database_utils.set_helper import CoClustering
from application.views.database_utils.spectral_biclustering import SpectralBiclustering
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data, one_hot_encoder
from application.views.database_utils.utils import decoding_categories, encoding_categories

class FeatureTest(unittest.TestCase):
    # def test_umap_simple(self):
    #     mnist = fetch_openml('mnist_784')
    #     print(mnist.data.shape)
    #     embedding = umap.UMAP(n_neighbors=10, min_dist=0.001)\
    #         .fit_transform(mnist.data)
    #     plt.scatter(embedding[:,0], embedding[:,1])
    #     plt.savefig("test/feature/feature-tsne.jpg")

    # def test_umap_feature(self):
    #     d = Data(config.coco17, suffix="step1")
    #     features = d.set_helper.image_feature
    #     for nn in [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:
    #         for dis in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5]:
    #             embedding = umap.UMAP(n_neighbors=10, min_dist=0.001)\
    #                 .fit_transform(features)
    #             plt.scatter(embedding[:,0], embedding[:,1])
    #             plt.savefig("test/feature/feature-umap-{}-{}.jpg".format(nn, dis))
    #             plt.close()
    #             np.save("test/feature/umap-embedding-{}-{}.npy".format(nn, dis), embedding)
    
    def test_kmeans(self):
        d = Data(config.coco17, suffix="step1")
        image_labels = d.get_category_pred(label_type="all", data_type="image")
        text_label = d.get_category_pred(label_type="all", data_type="text")
        features = d.set_helper.image_feature
        print("feature shape", features.shape)
        sizes = [256, 256, 256, 512, 1024, 512]
        split_points = [0]
        sum = 0
        feature_id = 3
        for i in sizes:
            sum = sum + i
            split_points.append(sum)
        print(split_points)
        feature = features[:, split_points[feature_id]: split_points[feature_id+1]]
        model = KMeans(100, init="k-means++",
                        n_init=10, n_jobs="deprecated",
                        random_state=123)
        model.fit(feature)
        labels = model.labels_
        np.save("test/feature/kmeans-3.npy".format(feature_id), labels)

        a = 1
    
    def test_evaluate_kmeans(self):
        # kmeans_result = "feature/kmeans-3.npy"
        # kmeans_result = "mismatch/constrained-kmeans-3.npy"
        kmeans_result = "mismatch/max-3000-constrained-kmeans-3.npy"
        d = Data(config.coco17, suffix="step1")
        image_labels = d.get_category_pred(label_type="all", data_type="image")
        text_labels = d.get_category_pred(label_type="all", data_type="text")
        kmeans = np.load("test/" + kmeans_result)
        mismatch = []
        counts = []
        for i in range(100):
            idxs = np.array(range(len(kmeans)))[kmeans == i]
            img = image_labels[idxs]
            text = text_labels[idxs]
            mm = (img!=text).sum()
            counts.append(len(idxs))
            mismatch.append(mm)
        mismatch = np.array(mismatch)
        pos = np.array(range(len(mismatch)))
        width = 0.25
        plt.bar(pos, counts, width, color = '#FF0000')
        plt.bar(pos + width, mismatch, width, color = '#6699CC')
        plt.savefig("test/{}_mismatch.jpg".format(kmeans_result))
        plt.close()
        a = 1

    def test_check_large_cluster(self):
        kmeans_result = "feature/kmeans-3.npy"
        # kmeans_result = "mismatch/constrained-kmeans-3.npy"
        d = Data(config.coco17, suffix="step1")
        image_labels = d.get_category_pred(label_type="all", data_type="image")
        text_labels = d.get_category_pred(label_type="all", data_type="text")
        kmeans = np.load("test/" + kmeans_result)
        features = d.set_helper.image_feature
        print("feature shape", features.shape)
        sizes = [256, 256, 256, 512, 1024, 512]
        split_points = [0]
        sum = 0
        feature_id = 3
        for i in sizes:
            sum = sum + i
            split_points.append(sum)
        print(split_points)
        feature = features[:, split_points[feature_id]: split_points[feature_id+1]]
        mismatch = (image_labels!=text_labels).sum(axis=1)
        idxs = np.array(range(len(kmeans)))[kmeans == 28]
        feature = feature[idxs]
        mismatch = mismatch[idxs]
        
        for i in range(2,10):
            model = KMeans(i, init="k-means++",
                            n_init=10, n_jobs="deprecated",
                            random_state=123)
            model.fit(feature)
            labels = model.labels_
            for j in range(i):
                m = mismatch[labels==j].sum()
                length = (labels==j).sum()
                print(m, length, m / length)
            print("***********************************")
        a = 1

    def test_cluster_performance(self):
        d = Data(config.coco17, suffix="step1")
        detect_eval = pickle.loads(open(os.path.join(d.data_root, \
            "detect_eval.pkl"), "rb").read())
        kmeans = np.load("test/feature/kmeans-3.npy")
        for i in range(100):
            idxs = np.array(range(len(kmeans)))[kmeans == i]
            res = [detect_eval[d.ids[j]] for j in idxs]
            res = [[k for k in r if k[1] > 0.5] for r in res]
            tp = [np.array(r)[:,0].sum() for r in res if len(r) > 0 ]
            fp = [len(r) - np.array(r)[:,0].sum() for r in res if len(r) > 0 ]
            # gt = [len(d.set_helper.get_anno_bbox_result(j)) for j in idxs]
            gt = []
            for j in idxs:
                try:
                    gt.append(len(d.set_helper.get_anno_bbox_result(int(j))))
                except:
                    a = 1
            pre = sum(tp) / (sum(tp) + sum(fp))
            rec = sum(tp) / sum(gt)
            print(i, pre, rec)
            a = 1
        a = 1

    def test_coclustering_by_clusters(self):
        kmeans = np.load("test/feature/kmeans-3.npy")
        d = Data(config.coco17, suffix="step1")

        class_name = d.class_name
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

        text_feature = np.load("test/word_embedding/word_feature.npy")
        text_feature = text_feature[1:]
        
        # normalization
        R = R[1:, :]
        class_name = class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.4)

        clf = CoClustering()
        k1, k2 = [12, 12]
        C1, C2 = clf.fit(R, text_feature, k1, k2)
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

        # normalization
        R = R[1:, :]
        class_name = class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.4)

        # coclustering 
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
        
        for i in range(k2):
            selected = model.column_labels_ == i
            # print("{}: total num of selected {}".format(i, sum(selected)))
            # print(np.array(range(100))[selected])
            print(cluster_mismatch[selected], "**", cluster_mismatch[selected].sum())

        Row = one_hot_encoder(model.row_labels_)
        Col = one_hot_encoder(model.column_labels_)
        S = np.dot(np.dot(Row.T, R), Col)

        # visualization 
        sns.set(font_scale=0.5)
        sns.heatmap(RR, yticklabels=np.array(class_name)[idx1])
        plt.savefig("test/feature/cluster_R.jpg")
        plt.close()

        a = 1

    def test_tsne(self):
        d = Data(config.coco17, suffix="step1")
        features = d.set_helper.image_feature
        sizes = [256, 256, 256, 512, 1024, 512]
        split_points = [0]
        sum = 0
        for i in sizes:
            sum = sum + i
            split_points.append(sum)
        print("split_points", split_points)
        for i in range(len(sizes)):
            sub_feature = features[:, split_points[i]: ]
            tsne = TSNE(n_components=2,random_state=15, verbose=1)
            embedding = tsne.fit_transform(sub_feature)
            plt.scatter(embedding[:,0], embedding[:,1])
            plt.savefig("test/feature/feature-tsne-{}-6.jpg".format(i))
            plt.close()
            np.save("test/feature/tsne-embedding-{}-6.npy".format(i), embedding)
            a = 1

if __name__ == '__main__':
    unittest.main()