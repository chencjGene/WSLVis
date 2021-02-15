import numpy as np
import json
import os
from tqdm import tqdm
from random import choice
from sklearn.cluster import KMeans
from time import time

from ..database_utils.utils import decoding_categories, encoding_categories
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import json_load_data, json_save_data 

class CoClustering(object):
    def __init__(self):
        None

    def kmeans(self, M, k):
        kmeans = KMeans(n_clusters=k, random_state=12).fit(M)
        cluster = kmeans.labels_
        res = np.zeros(M.shape)
        res[np.array(range(M.shape[0])), cluster] = 1
        return res

    def eigenvector(self, M, k):
        eigenvalues, eigenvectors = np.linalg.eig(M)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
        real = eigenvectors.real
        imag = eigenvectors.imag
        # assert (imag ** 2).sum() < 1e-6
        # print("image sum ", (imag ** 2).sum())
        return eigenvectors[:, :k]

    def random_orthonormal_matrix(self, n, k):
        M = np.zeros((n, k))
        cluster = np.random.randint(0, k, n)
        M[np.array(range(n)), cluster] = 1
        norm = M.sum(axis=0) ** 0.5
        norm = norm.reshape(1,-1)
        M = M / norm
        return M

    def fit(self, R, text_feature, k1, k2):
        # init 
        w_t = 0
        n1, n2 = R.shape
        C1 = self.random_orthonormal_matrix(n1, k1)
        C2 = self.random_orthonormal_matrix(n2, k2)
        pre_C1 = C1.copy()
        pre_C2 = C2.copy()
        for i in range(100):
            t0 = time()
            tmp = np.dot(R, C2)
            tmp = np.dot(tmp, C2.T)
            M1 = np.dot(tmp, R.T) + w_t * np.dot(text_feature, text_feature.T)
            C1 = self.eigenvector(M1, k1)
            tmp = np.dot(R.T, C1)
            tmp = np.dot(tmp, C1.T)
            M2 = np.dot(tmp, R)
            C2 = self.eigenvector(M2, k2)
            err1 = ((C1 - pre_C1)**2).sum()
            err2 = ((C2 - pre_C2)**2).sum()
            print("iter {}, time cost: {}, err1: {}, err2: {}" \
                .format(i, time() - t0, err1, err2))
            pre_C1 = C1.copy()
            pre_C2 = C2.copy()
        print("C1 imag", (abs(C1.imag)).sum())
        print("C2 imag", (abs(C2.imag)).sum())
        C1 = self.kmeans(C1.real, k1)
        C2 = self.kmeans(C2.real, k2)
        return C1, C2
        
    def rearrange(self, R, C1, C2):
        n1, k1 = C1.shape
        n2, k2 = C2.shape
        cls1 = np.array(range(k1)).reshape(1, -1).repeat(axis=0, repeats=n1)
        cls2 = np.array(range(k2)).reshape(1, -1).repeat(axis=0, repeats=n2)
        cls1 = (C1 * cls1).sum(axis=1)
        cls2 = (C2 * cls2).sum(axis=1)
        idx1 = cls1.argsort()
        idx2 = cls2.argsort()
        R = R[idx1, :]
        R = R[:, idx2]
        return R

class SetHelper(object):
    def __init__(self, parent):
        self.parent = parent
        self.train_idx = self.parent.train_idx
        self.conn = self.parent.conn
        self.data_root = self.parent.data_root
        self.data_all_step_root = self.parent.data_all_step_root
        self.class_name = self.parent.class_name
        self.conf_thresh = 0.5
        self.sets = {}
        self.sampled_sets = {}
        
        self.width_height = json_load_data(os.path.join(self.data_all_step_root, \
            "width_height.json"))
        
        self._get_image_by_type()
        # self._graph_construction()
        self._load_image_feature()
        
        self.image_feature = np.load(os.path.join(self.data_root, "feature_train.npy"))

        a = 1

    def _load_image_feature(self):
        logger.info("begin load image feature")
        feature_path = os.path.join(self.data_root, "feature_train.npy")
        self.image_features = np.load(feature_path)
        logger.info("end load image feature")


    def get_image_type_feature(self, t):
        None

    def _get_image_by_type(self):
        filename = os.path.join(self.data_root, "image_by_type.json")
        if os.path.exists(filename):
            logger.info("using image_by_type.json buffer")
            self.image_by_type = json_load_data(filename)
            return 

        self.image_by_type = {}
        for idx in tqdm(self.train_idx):
            det = self.get_detection_result(idx)
            category = [d[-1] for d in det if d[-2] > self.conf_thresh]
            cat_str = encoding_categories(category)
            if cat_str not in self.image_by_type:
                self.image_by_type[cat_str] = []
            self.image_by_type[cat_str].append(int(idx))
        json_save_data(filename, self.image_by_type)

    def _graph_construction(self):
        logger.info("begin graph construction in set helper")
        all_types = self.get_all_set_name()
        types = {}
        # calculate out links
        for t in all_types:
            cats = decoding_categories(t)
            links = []
            for s in all_types:
                cats_of_s = decoding_categories(s)
                if set(cats_of_s) > set(cats):
                    links.append(s)
            image_list = self.get_image_list_by_type(t, scope="all")
            types[t] = {
                "type": t,
                "num": len(image_list),
                "selected_image": self.get_image_list_by_type(t, \
                    scope="selected", with_wh=True),
                "out_links": links,
                "in_links": []
            }
        # calculate in links
        for t in types:
            out_links = types[t]["out_links"]
            for s in out_links:
                types[s]["in_links"].append(t)
        
        
        self.sets = types
        selected_sets = [name for name in self.sets.keys() \
            if len(self.sets[name]["out_links"]) == 0]
        
        # hierarchy clustering
        while len(selected_sets) > 1:
            set1 = choice(selected_sets) # TODO
            selected_sets.remove(set1)
            set2 = choice(selected_sets) # TODO
            selected_sets.remove(set2)
            cats = decoding_categories(set1) + decoding_categories(set2)
            set_name = encoding_categories(cats)
            self.sets[set_name] = {
                "type": set_name,
                "num": 0,
                "selected_image": [], # TODO,
                "out_links": [],
                "in_links": list(set(self.sets[set1]["in_links"] + \
                    self.sets[set2]["in_links"])) + [set1, set2]
            }
            # self.sets[set1]["out_links"].append(set_name)
            # self.sets[set2]["out_links"].append(set_name)
            for s in self.sets[set_name]["in_links"]:
                self.sets[s]["out_links"].append(set_name)
            selected_sets.append(set_name)

        logger.info("finish graph construction in set helper")

    def _graph_sampling(self):
        for t in self.sets:
            self.sets[t]["tmp_out_links"] = self.sets[t]["out_links"].copy()
            self.sets[t]["visited"] = False
        selected_sets = [name for name in self.sets.keys() \
            if len(self.sets[name]["out_links"]) == 0]
        self.selected_sets = []
        while len(self.selected_sets) + len(selected_sets) < 10:
            selected_one_with_largest_gain = choice(selected_sets) # TODO
            self.sets[selected_one_with_largest_gain]["visited"] = True
            if self.sets[selected_one_with_largest_gain]["num"] > 0:
                self.selected_sets.append(selected_one_with_largest_gain)
            for s in self.sets[selected_one_with_largest_gain]["in_links"]:
                self.sets[s]["tmp_out_links"].remove(selected_one_with_largest_gain)
            selected_sets = [name for name in self.sets.keys() \
            if len(self.sets[name]["tmp_out_links"]) == 0 and self.sets[name]["visited"] is False]
            print("while", len(self.selected_sets), len(selected_sets))
        self._selected_sets = self.selected_sets + selected_sets
        self.selected_sets = {}
        for s in self._selected_sets:
            self.selected_sets[s] = self.sets[s]
        print(self.selected_sets.keys())
        return self.selected_sets

    def get_real_set(self):
        image_by_type = {}
        for idx in tqdm(self.train_idx):
            det = self.get_anno_bbox_result(idx)
            category = [d[-1] for d in det if d[-2] > self.conf_thresh]
            cat_str = encoding_categories(category)
            if cat_str not in image_by_type:
                image_by_type[cat_str] = []
            image_by_type[cat_str].append(int(idx))
        
        all_types = image_by_type.keys()
        types = []
        for t in all_types:
            if len(image_by_type[t]) > 20 and len(t) > 0:
                types.append(t)
        return image_by_type, types

    def get_real_image(self):
        image_by_type = {}
        for idx in tqdm(self.train_idx):
            det = self.get_anno_bbox_result(idx)
            category = [d[-1] for d in det if d[-2] > self.conf_thresh and d[-1] != 0]
            cat_str = encoding_categories(category)
            if cat_str not in image_by_type:
                image_by_type[cat_str] = []
            image_by_type[cat_str].append(int(idx))
            
        all_types = image_by_type.keys()
        type_size = []
        type_name = []
        for t in all_types:
            type_name.append(t)
            type_len = len(image_by_type[t])
            if len(t) == 0 or len(decoding_categories(t)) < 2:
                type_len = 1
            type_size.append(type_len)
        type_size = np.array(type_size)
        type_name = np.array(type_name)
        idx = type_size.argsort()[::-1][:100]
        type_name = type_name[idx]
        return image_by_type, type_name

    def get_set(self):
        # self.sampled_sets = self._graph_sampling()
        # return self.sampled_sets
        self.sets = self.get_all_set_name()
        return self.sets

    def get_image_type_feature(self, image_type):
        None

    def get_all_set_name(self):
        all_types = self.image_by_type.keys()
        types = []
        for t in all_types:
            if len(self.image_by_type[t]) > 50 and len(t) > 0:
                types.append(t)
        return types

    def get_detection_result(self, idx):
        cursor = self.conn.cursor()
        sql = "select detection from annos where id = ?"
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0][0]
        res = json.loads(res)
        return res

    def get_anno_bbox_result(self, idx):
        cursor = self.conn.cursor()
        sql = "select bbox from annos where id = ?"
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0][0]
        res = json.loads(res)
        return res


    def get_image_list_by_type(self, t, scope="selected", with_wh = False):
        def add_width_height(idx):
            w, h = self.width_height[idx]
            detection = self.get_detection_result(idx)
            detection = np.array(detection)
            conf_detection = detection[detection[:, -2] > self.conf_thresh].astype(np.float32)
            conf_detection[:, 0] /= w
            conf_detection[:, 2] /= w
            conf_detection[:, 1] /= h
            conf_detection[:, 3] /= h
            conf_detection = np.round(conf_detection, 3)
            return {"idx": idx, "w": w, "h": h, "d": conf_detection.tolist()}
        if scope == "all":
            if with_wh:
                return [add_width_height(i) for i in self.image_by_type[t]]
            else:
                return self.image_by_type[t]
        elif scope == "selected":
            if with_wh:
                return [add_width_height(i) for i in self.image_by_type[t][-10:]]
            else:
                return self.image_by_type[t][-10:]
