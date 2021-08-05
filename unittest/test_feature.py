import numpy as np
import umap 
import matplotlib.pyplot as plt
import unittest
import pickle
import os 
import seaborn as sns
from tqdm import tqdm

from sklearn.datasets import load_digits
from sklearn.datasets import fetch_openml
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, MiniBatchKMeans

from application.views.database_utils import Data
from application.views.database_utils.set_helper import CoClustering
from application.views.database_utils.spectral_biclustering import SpectralBiclustering
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data, one_hot_encoder, pickle_save_data
from application.views.database_utils.utils import decoding_categories, encoding_categories

class FeatureTest(unittest.TestCase):
    def test_kmeans(self):
        d = Data(config.coco17, step=1)
        image_labels = d.get_category_pred(label_type="all", data_type="image")
        text_label = d.get_category_pred(label_type="all", data_type="text")
        feature = d.get_image_feature()
        # feature = feature[:100,:]
        sse = {}
        for k in tqdm(range(2, 300)):
        # for k in tqdm(range(2, 10)):
            model = KMeans(k, init="k-means++",
                            n_init=10, n_jobs="deprecated",
                            random_state=123)
            model.fit(feature)
            # labels = model.labels_
            sse[k] = model.inertia_
        plt.figure()
        plt.plot(list(sse.keys()), list(sse.values()))
        plt.xlabel("Number of cluster")
        plt.ylabel("SSE")
        plt.savefig("test/feature/sse_plot.jpg")
        plt.close()
        # np.save("test/feature/kmeans-3.npy".format(feature_id), labels)

        a = 1

    def test_text_kmeans(self):
        d = Data(config.coco17, step=1)
        feature = d.get_text_feature()
        sse = {}
        for k in tqdm(range(2,20)):
            model = KMeans(k, init="k-means++",
                            n_init=10, n_jobs="deprecated",
                            random_state=123)
            model.fit(feature)
            sse[k] = model.inertia_
        plt.figure()
        plt.plot(list(sse.keys()), list(sse.values()))
        plt.xlabel("Number of cluster")
        plt.ylabel("SSE")
        plt.savefig("test/feature/sse_text_plot.jpg")
        pickle_save_data("test/feature/sse_text.pkl", sse)
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
    suite = unittest.TestSuite()
    suite.addTest(FeatureTest("test_kmeans"))
    
    # # test all cases
    # suite =  unittest.TestLoader().loadTestsFromTestCase(CoClusteringTest)
    unittest.TextTestRunner(verbosity=2).run(suite)