import numpy as np
import os

from sklearn.cluster import KMeans, MiniBatchKMeans

from ..utils.log_utils import logger
from ..utils.helper_utils import json_load_data, json_save_data
from ..utils.helper_utils import pickle_save_data, pickle_load_data
from ..database_utils.data_database import Data
# from ..database_utils.data import Data
try:
    from ..constrained_kmeans.k_means_constrained_ import KMeansConstrained
except:
    None
    
from .coclustering import CoClustering
from .tree_helper import TextTreeHelper, TreeHelper, ImageTreeHelper


class WSLModel(object):
    def __init__(self, dataname=None, step=0, config=None):
        self.dataname = dataname
        self.step = step
        if config:
            self.config = config
        else:
            self.config = {
                "text_k": 12,
                "image_k": 12,
                "pre_k": 100
            }
        if dataname is None:
            return 
        self._init()
    
    def _init(self):
        logger.info("current config of model: dataname-{}, step-{}, text_k-{}, image_k-{}, pre_k-{}".format(self.dataname, self.step,\
                self.config["text_k"], self.config["image_k"], self.config["pre_k"]))
        self._init_data()
        self.data_root = self.data.data_root
        self.data_all_step_root = self.data.data_all_step_root
        self.buffer_path = os.path.join(self.data_root, "model.pkl")
        self.pre_clustering = KMeansConstrained(n_init=1, n_clusters=self.config["pre_k"],
            size_min=1, size_max=3000, random_state=0)
        self.cluster_name = ["img_cluster_"+ str(i) for i in range(self.config["pre_k"])]
        self.coclustering = CoClustering(self.config["text_k"], \
            self.config["image_k"], 0, verbose=0) # TODO: 
        self.text_tree_helper = TextTreeHelper()
        self.image_tree_helper = ImageTreeHelper()
        

    def _init_data(self):
        self.data = Data(self.dataname, self.step)

    def reset(self, dataname, step, config):
        self.dataname = dataname
        self.step = step
        self._init()

    def run(self):
        self.data.run()

        # pre-kmeans
        self._run_pre_clustering()
        
        # coclustering
        # self._run_coclustering()

        # hierarchical coclustering
        self._run_hierarchical_coclustering()
    
    def _run_pre_clustering(self):
        pre_clustering_result_file = os.path.join(self.data_root, "pre_clustering.npy")
        if os.path.exists(pre_clustering_result_file):
            self.pre_clustering_res = np.load(pre_clustering_result_file)
            return
        image_labels = self.data.get_category_pred(label_type="all", data_type="image")
        text_labels = self.data.get_category_pred(label_type="all", data_type="text")
        mismatch = (image_labels!=text_labels).sum(axis=1)
        features = self.data.get_image_feature()
        self.pre_clustering.fit_predict(features, mismatch)
        self.pre_clustering_res = self.pre_clustering.labels_
        np.save(pre_clustering_result_file, self.pre_clustering_res)
        return

    def _run_coclustering(self):
        self.R = self.get_R()
        text_feature = self.data.get_text_feature()[1:]

        self.C1, self.C2 = self.coclustering.fit(self.R, text_feature)
        self.text_labels = np.dot(self.C1, \
            np.array(range(self.config["text_k"])).reshape(-1,1)).reshape(-1)
        self.image_labels = np.dot(self.C2, \
            np.array(range(self.config["image_k"])).reshape(-1,1)).reshape(-1)

    def _kmeans(self, X, k):
        logger.info("performing kmeans with k is {}".format(k))
        # model = KMeans(k, init="k-means++",
        #                 n_init=10, n_jobs="deprecated",
        #                 random_state=123)
        model = KMeans(n_clusters=k, random_state=12)
        model.fit(X)
        labels = model.labels_
        return labels

    def _hierarchical_coclustering(self, tree, X):
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            descendants_idx = node["descendants_idx"]
            des_X = X[np.array(descendants_idx), :]
            if len(descendants_idx) > 6:
                if node["name"] == "root" and node["type"] == "text":
                    k = 10
                elif node["name"] == "root" and node["type"] == "image":
                    k = 10
                else:
                    k = 3
                # run clustering algorithm
                labels = self._kmeans(des_X, k)
                # create tree node for each cluster under this node
                children = []
                for i in range(k):
                    internal_node = {
                        "type": node["type"],
                        "name": "internal",
                        "descendants_idx": np.array(descendants_idx)[labels==i].tolist()
                    }
                    children.append(internal_node)
                node["children"] = children
            else:
                node["children"] = []
            visit_node.extend(node["children"])
        return tree

    def _post_processing_hierarchy(self, tree, name_list):
        shift = 0
        if tree["type"] == "text":
            shift = 1
            node = {
                "type": "text",
                "name": "person",
                "children": []
            }
            tree["children"].append(node)
            tree["descendants_idx"] = [-1] + tree["descendants_idx"]
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            if "descendants_idx" in node:
                descendants_idx = node["descendants_idx"]
                descendants_idx = [i + shift for i in descendants_idx]
                node["descendants_idx"] = descendants_idx
            if len(node["children"]) == 0 and "descendants_idx" in node:
                descendants_idx = node["descendants_idx"]
                for idx in descendants_idx:
                    name = name_list[idx]
                    leaf_node = {
                        "type": "text",
                        "name": str(name),
                        "children": [],
                    }
                    node["children"].append(leaf_node)
                # del node["descendants_idx"]
            visit_node.extend(node["children"])
        return tree

    def _run_hierarchical_coclustering(self):
        self.R = self.get_R()
        text_feature = self.data.get_text_feature()[1:]
        text_w, image_h = self.coclustering._fit(self.R, text_feature)
        image_h = image_h.T
        text_tree = {
            "type": "text",
            "name": "root",
            "descendants_idx":list(range(text_w.shape[0])),
        }
        image_tree = {
            "type": "image",
            "name": "root",
            "descendants_idx": list(range(image_h.shape[0]))
        }
        text_tree = self._hierarchical_coclustering(text_tree, text_w)
        image_tree = self._hierarchical_coclustering(image_tree, image_h)
        self.text_tree = self._post_processing_hierarchy(text_tree, self.data.class_name)
        self.image_tree = self._post_processing_hierarchy(image_tree, self.cluster_name)

        self.text_tree_helper.update(self.text_tree, self.data.class_name)
        self.image_tree_helper.update(self.image_tree, self.cluster_name)
        self.data.get_precision_and_recall()
        self.text_tree_helper.assign_precision_and_recall(\
            self.data.precision, self.data.recall)

        a = 1

    def get_R(self, exclude_person=True):
        # processing R
        class_name = self.data.class_name
        kmeans = self.pre_clustering_res
        R_path = os.path.join(self.data_root, "cluster_R.npy")
        origin_R = np.zeros((len(class_name), len(np.unique(kmeans))))
        if os.path.exists(R_path):
            origin_R = np.load(R_path)
        else:
            print("R.shape", origin_R.shape)
            for i in range(self.config["pre_k"]):
                r = origin_R[:,i]
                idxs = np.array(range(len(kmeans)))[kmeans == i]
                for j in idxs:
                    res = self.data.get_detection_result(int(j)) 
                    for det in res:
                        if det[-2] > 0.5:
                            r[det[-1]] += 1
                origin_R[:, i] = r
            np.save(R_path, origin_R)

        
        # normalization
        R = origin_R[1:, :].copy()
        class_name = self.data.class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.41)

        if exclude_person:
            return R
        else:
            origin_R = origin_R / R.max()
            origin_R = np.power(origin_R, 0.41)
            return origin_R

    def get_current_hypergraph(self):
        mat = {
            "text_tree": self.text_tree,
            "image_tree": self.image_tree,
            "cluster_association_matrix": self.get_R(False).tolist()
        }
        return mat

    def save_model(self, path=None):
        buffer_path = self.buffer_path
        if path:
            buffer_path = path
        tmp_data = self.data
        self.data = None
        pickle_save_data(buffer_path, self)
        self.data = tmp_data

    def load_model(self, path=None):
        buffer_path = self.buffer_path
        if path:
            buffer_path = path
        self = pickle_load_data(buffer_path)
        self.data = Data(self.dataname, self.step)
    
    def buffer_exist(self, path=None):
        buffer_path = self.buffer_path
        if path:
            buffer_path = path
        if os.path.exists(buffer_path):
            return True
        else:
            return False
        