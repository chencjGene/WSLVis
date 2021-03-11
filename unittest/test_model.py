import unittest
import numpy as np
import os
import scipy.io as sio
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from tqdm import tqdm
from time import time
from itertools import chain

from sklearn.metrics import confusion_matrix, precision_score, recall_score
from sklearn.datasets import make_checkerboard
from sklearn.cluster import SpectralBiclustering
from sklearn.metrics import consensus_score
from sklearn.utils.extmath import (make_nonnegative, randomized_svd,
                             safe_sparse_dot)
from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN
from sklearn.metrics import pairwise_distances

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
        m = pickle_load_data(m.buffer_path)
        m._init_data()
        m.text_tree_helper.import_from_file(os.path.join(m.data_root, \
                "clustering_hierarchy.json"))
        class_name = m.data.class_name
        all_labels = [m.text_tree_helper.get_all_leaf_descendants_ids(n) \
            for n in m.text_tree_helper.tree["children"][:-1]]
        descendants = m.text_tree_helper\
            .get_all_leaf_descendants(m.text_tree_helper.tree)
        text_labels = [d["id"] for d in descendants[::-1]]
        image_labels = [d["cluster_idxs"] for d in m.image_cluster_list]
        image_names = [ np.ones(len(d)).astype(int) * idx for idx, d in enumerate(image_labels)]
        image_labels = list(chain(*image_labels))
        image_names = list(chain(*image_names))
        R = m.get_R(exclude_person=False, detection=False)
        R = R[text_labels, :][:,image_labels]
        sns.set(font_scale=0.5)
        sns.heatmap(R, yticklabels=np.array(class_name)[text_labels],
            xticklabels=image_names)
        plt.show()
        plt.savefig("test/mismatch/coclustering_result.jpg")
        plt.close()

        CAM = m.get_cluster_association_matrix()[0].T
        CAM = CAM[text_labels]

        sns.heatmap(CAM, yticklabels=np.array(class_name)[text_labels])
        plt.show()
        plt.savefig("test/mismatch/CAM.jpg")
        plt.close()

        for i in range(m.config["text_k"]):
            selected = np.array(all_labels[i])
            # print("total num of selected", sum(selected))
            print(np.array(class_name)[selected])
        a = 1

    def test_accuracy(self):
        dataname = "COCO17"
        step = 0
        m = WSLModel(dataname=config.coco17, step=step)
        m = WSLModel(dataname=dataname, step=step)
        m = pickle_load_data(m.buffer_path)
        m.dataname = dataname
        m.step = step
        m._init_data()
        class_name = m.data.class_name
        cluster_id = 8
        image_ids = np.array(m.image_ids_of_clusters[cluster_id])
        image_labels = m.data.get_category_pred(label_type="all", \
            data_type="image", threshold=0.5)
        text_labels = m.data.get_category_pred(label_type="val", data_type="text-only")
        gt = m.data.get_groundtruth_labels(label_type="val")
        ps = []
        rs = []
        for i in range(len(class_name)):
            p = precision_score(gt[:, i], text_labels[:, i])
            r = recall_score(gt[:, i], text_labels[:, i])
            ps.append(p)
            rs.append(r)
            print(class_name[i], p, r)
        print("mean", np.array(ps).mean(), np.array(rs).mean())

        val_res = os.path.join(config.raw_data_root, "COCO17", "step0", "val_result_text.pkl")
        val_res = pickle_load_data(val_res)
        
        id_map = {}
        for d in val_res:
            image_id = d["image_id"][0].decode()
            id_map[image_id] = d

        preds = []
        for i in range(text_labels.shape[0]):
            img_id = m.data.ids[m.data.val_idx[i]]
            d = id_map[str(img_id)]
            label = d["label"]
            pred = (d["logits"] > 0).astype(int).reshape(-1)
            preds.append(pred)
            if (text_labels[i] != pred).sum() > 0 or (gt[i]!=label).sum() > 0:
                a = 1
        preds = np.array(preds)
        ps = []
        rs = []
        for i in range(len(class_name)):
            p = precision_score(gt[:, i], text_labels[:, i])
            r = recall_score(gt[:, i], text_labels[:, i])
            ps.append(p)
            rs.append(r)
            print(class_name[i], p, r)
        print("mean", np.array(ps).mean(), np.array(rs).mean())



        # selected_image_labels = image_labels[image_ids][:, 59]
        # selected_text_labels = text_labels[image_ids][:, 59]
        # selected_gt = gt[image_ids][:, 59]
        # mismatched = (selected_image_labels != selected_text_labels)

        a = 1

    def test_grid_layout(self):
        m = WSLModel(dataname=config.coco17, step=1)
        m = pickle_load_data(m.buffer_path)
        m.update_data_root(config.coco17, 1)
        m._init_data()
        m.set_focus_image_cluster(4)
        m.get_grid_layout(0, 0, 1, 1, -1)
        a = 1

    def test_rank(self):
        m = WSLModel(dataname=config.coco17, step=1)
        m.run()
        # res = m.get_rank(4)

        image_ids = m.image_ids_of_clusters[4]
        features = m.data.get_image_feature()[np.array(image_ids)]
        selected_idxs = [219, 261, 478, 604, 774, 2295, 2337, 2678, 3251, 72, 94, 181, 394, 1204, 1262, 1697, 1735, 1747, 2002, 2025]
        selected_ids = [30809, 37215, 68209, 86496, 106585, 36553, 41444, 90739, 52703, 10416, 14556, 25706, 55027, 35357, 40251, 78098, 82384, 83946, 109110, 111414]
        # labels = [-1, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        pd = pairwise_distances(features)
        g1 = np.array(selected_idxs[:9])
        g2 = np.array(selected_idxs[9:])
        d1 = pd[g1,:][:,g1]
        d2 = pd[g2,:][:,g2]
        for i in range(len(selected_idxs)):
            idx = selected_idxs[i]
            d = pd[idx,:]
            sorted_idxs = d.argsort()[:20]
            intersec = set(selected_idxs) & set(sorted_idxs)
            print(intersec)

        # model = DBSCAN(eps=2, min_samples=2).fit(features)
        # labels = model.labels_
        # sio.savemat("test/feature/feature_4.mat", {"data": features})
        # R = np.zeros((len(image_ids), 65))
        # for idx, img_id in enumerate(image_ids):
        #     res = m.data.get_detection_result(int(img_id))
        #     for det in res:
        #         if det[-2] > m.data.conf_thresh:
        #             R[idx, det[-1]] = 1
        # R = R / (R.sum(axis=1).reshape(-1, 1) + 1e-12)
        # s = lap_score(R.T)
        a = 1

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(CoClusteringTest("test_accuracy"))
    
    # # test all cases
    # suite =  unittest.TestLoader().loadTestsFromTestCase(CoClusteringTest)
    unittest.TextTestRunner(verbosity=2).run(suite)