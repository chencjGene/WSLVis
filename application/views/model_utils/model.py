import numpy as np
import os

from ..utils.log_utils import logger
from ..database_utils.data_database import Data
# from ..database_utils.data import Data
from ..constrained_kmeans.k_means_constrained_ import KMeansConstrained

from .coclustering import CoClustering


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
        self.data = Data(self.dataname, self.step)
        self.data_root = self.data.data_root
        self.data_all_step_root = self.data.data_all_step_root
        self.pre_clustering = KMeansConstrained(n_init=1, n_clusters=self.config["pre_k"],
            size_min=1, size_max=3000, random_state=0)
        self.coclustering = CoClustering(self.config["text_k"], \
            self.config["image_k"], 0) # TODO: 

    def reset(self, dataname, step, config):
        self.dataname = dataname
        self.step = step
        self._init()


    def run(self):
        self.data.run()

        # pre-kmeans
        self._run_pre_clustering()
        
        # coclustering
        self._run_coclustering()
    
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

    def get_R(self):
        # processing R
        class_name = self.data.class_name
        kmeans = self.pre_clustering_res
        R_path = os.path.join(self.data_root, "cluster_R.npy")
        R = np.zeros((len(class_name), len(np.unique(kmeans))))
        if os.path.exists(R_path):
            R = np.load(R_path)
        else:
            print("R.shape", R.shape)
            for i in range(self.config["pre_k"]):
                r = R[:,i]
                idxs = np.array(range(len(kmeans)))[kmeans == i]
                for j in idxs:
                    res = self.data.get_detection_result(int(j)) 
                    for det in res:
                        if det[-2] > 0.5:
                            r[det[-1]] += 1
                R[:, i] = r
            np.save(R_path, R)

        
        # normalization
        R = R[1:, :]
        class_name = self.data.class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.41)
        return R

    def _run_coclustering(self):
        self.R = self.get_R()
        text_feature = self.data.get_text_feature()[1:]

        self.C1, self.C2 = self.coclustering.fit(self.R, text_feature)
        self.text_labels = np.dot(self.C1, \
            np.array(range(self.config["text_k"])).reshape(-1,1)).reshape(-1)
        self.image_labels = np.dot(self.C2, \
            np.array(range(self.config["image_k"])).reshape(-1,1)).reshape(-1)
