import numpy as np
import os

from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.manifold import TSNE

from ..utils.log_utils import logger
from ..utils.config_utils import config
from ..utils.helper_utils import json_load_data, json_save_data
from ..utils.helper_utils import pickle_save_data, pickle_load_data, check_dir
from ..database_utils.data_database import Data
# from ..database_utils.data import Data
try:
    from ..constrained_kmeans.k_means_constrained_ import KMeansConstrained
except:
    None
    
from .coclustering import CoClustering
from .tree_helper import TextTreeHelper, TreeHelper, ImageTreeHelper
from .ranker import ImageRanker
from .sampler import Sampler


class WSLModel(object):
    def __init__(self, dataname=None, step=0, config=None):
        self.dataname = dataname
        self.step = step
        if config:
            self.config = config
        else:
            self.config = {
                "step": 1,
                "text_k": 9,
                "image_k": 9,
                "pre_k": 100,
                "weight": 1
            }
        if dataname is None:
            return 
        self._init()
    
    def update_data_root(self, dataname, step):
        self.step = step
        suffix = "step" + str(step)
        self.data_all_step_root = os.path.join(config.data_root, dataname)
        self.data_root = os.path.join(config.data_root, self.dataname, suffix)
        self.buffer_path = os.path.join(self.data_root, "model.pkl")

    def _init(self):
        logger.info("current config of model: dataname-{}, step-{}, text_k-{}, image_k-{}, pre_k-{}".format(self.dataname, self.step,\
                self.config["text_k"], self.config["image_k"], self.config["pre_k"]))
        # data 
        self._init_data()
        self.data_root = self.data.data_root
        self.data_all_step_root = self.data.data_all_step_root
        self.buffer_path = os.path.join(self.data_root, "model.pkl")
        self.hiera = ""

        # clustering model
        # self.pre_clustering = KMeansConstrained(n_init=1, n_clusters=self.config["pre_k"],
            # size_min=1, size_max=3000, random_state=0)
        self.image_cluster_name = ["img_cluster_"+ str(i) for i in range(self.config["pre_k"])]
        self.coclustering = CoClustering(self.config["text_k"], \
            self.config["image_k"], self.config["weight"], verbose=0) 
        self.text_tree_helper = TextTreeHelper(data_root=self.data_root)
        # self.samplers = [Sampler(id=i) for i in range(self.config["image_k"])]

        # ranking model
        self.ranker = ImageRanker()
        self.rank_res = {}
        
    def _init_data(self):
        self.data = Data(self.dataname, self.step)

    def reset(self, dataname, step, config):
        self.dataname = dataname
        self.step = step
        self._init()

    def update_hiera(self, hiera):
        self.hiera = hiera

    def run(self):
        self.data.run()

        # pre-kmeans
        self._run_pre_clustering()
        
        # coclustering
        # self._run_coclustering()

        # hierarchical coclustering
        self._run_hierarchical_coclustering()

        [self.get_rank(i) for i in range(len(self.image_cluster_list))]
    
    def _run_pre_clustering(self):
        pre_clustering_result_file = os.path.join(self.data_root, "pre_clustering.npy")
        if os.path.exists(pre_clustering_result_file):
            self.pre_clustering_res = np.load(pre_clustering_result_file)
            return
        image_labels = self.data.get_category_pred(label_type="all", data_type="image")
        text_labels = self.data.get_category_pred(label_type="all", data_type="text")
        self.mismatch = (image_labels!=text_labels).sum(axis=1)
        features = self.data.get_image_feature()
        self.pre_clustering.fit_predict(features, self.mismatch)
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

    def _image_cluster(self, X, k):
        logger.info("performing kmeans with k is {}".format(k))
        model = KMeans(n_clusters=k, random_state=12)
        model.fit(X)
        labels = model.labels_
        image_cluster_list = []
        for i in range(k):
            idxs = np.array(range(len(labels)))[labels==i]
            image_cluster_list.append({
                "cluster_idxs": idxs.tolist(),
                "id": i
            })
        return image_cluster_list

    def _hierarchical_coclustering(self, tree, X):
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            descendants_idx = node["descendants_idx"]
            des_X = X[np.array(descendants_idx), :]
            if len(descendants_idx) > 6:
                if node["name"] == "root" and node["type"] == "text":
                    k = self.config["text_k"]
                elif node["name"] == "root" and node["type"] == "image":
                    k = self.config["image_k"]
                else:
                    k = 2
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
            visit_node.extend(node["children"])
        return tree

    def _run_hierarchical_coclustering(self):
        self.R = self.get_R()
        text_clustering_path = os.path.join(self.data_root, "clustering_hierarchy-{}.json".format(self.hiera))
        image_clustering_path = os.path.join(self.data_root, "image_clustering.pkl")
        if os.path.exists(text_clustering_path) and os.path.exists(image_clustering_path):
            logger.info("loading clustering result from buffer")
            logger.info("{}".format(text_clustering_path))
            self.text_tree = json_load_data(text_clustering_path)
            self.image_cluster_list = pickle_load_data(image_clustering_path)
        else:
            text_feature = self.data.get_text_feature()[1:]
            text_w, image_h = self.coclustering._fit(self.R, text_feature)
            image_h = image_h.T
            text_tree = {
                "type": "text",
                "name": "root",
                "descendants_idx":list(range(text_w.shape[0])),
            }
            text_tree = self._hierarchical_coclustering(text_tree, text_w)
            self.text_tree = self._post_processing_hierarchy(text_tree, self.data.class_name)
            self.image_cluster_list = self._image_cluster(image_h, self.config["image_k"])
            pickle_save_data(image_clustering_path, self.image_cluster_list)
            json_save_data(text_clustering_path, text_tree)


        self._get_image_ids_of_clusters()
        [self.get_rank(i) for i in range(len(self.image_cluster_list))]
        self.text_tree_helper.update(self.text_tree, self.data.class_name)

        
        # self.data.get_precision_and_recall()
        # self.text_tree_helper.assign_precision_and_recall(\
        #     self.data.precision, self.data.recall)

        a = 1

    def _get_image_ids_of_clusters(self):
        logger.info("begin get_image_ids_of_clusters")
        self.image_ids_of_clusters = {}
        for i in range(len(self.image_cluster_list)):
            pre_cluster_ids = self.image_cluster_list[i]["cluster_idxs"]
            image_ids = []
            for cluster_id in pre_cluster_ids:
                ids = np.array(range(len(self.pre_clustering_res)))
                ids = ids[self.pre_clustering_res==cluster_id]
                image_ids = image_ids + ids.tolist()
            self.image_ids_of_clusters[i] = image_ids
        logger.info("end get_image_ids_of_clusters")

    def get_R(self, exclude_person=True, detection=True):
        # processing R
        class_name = self.data.class_name
        kmeans = self.pre_clustering_res
        suffix = ""
        if not detection:
            suffix = "_gt"
        R_path = os.path.join(self.data_root, "cluster_R{}.npy".format(suffix))
        origin_R = np.zeros((len(class_name), len(np.unique(kmeans))))
        if os.path.exists(R_path):
            origin_R = np.load(R_path)
        else:
            print("R.shape", origin_R.shape)
            for i in range(self.config["pre_k"]):
                r = origin_R[:,i]
                idxs = np.array(range(len(kmeans)))[kmeans == i]
                for j in idxs:
                    if detection:
                        res = self.data.get_detection_result(int(j)) 
                    else:
                        res = self.data.get_anno_bbox_result(int(j)) 
                    for det in res:
                        if det[-2] > 0.5:
                            r[det[-1]] += 1
                origin_R[:, i] = r
            np.save(R_path, origin_R)

        
        # normalization
        R = origin_R[1:, :].copy()
        class_name = self.data.class_name[1:]
        R = R / R.max()
        R = np.power(R, 0.40)

        if exclude_person:
            return R
        else:
            origin_R = origin_R / R.max()
            origin_R = np.power(origin_R, 0.40)
            return origin_R

    def get_cluster_association_matrix(self):
        origin_mat = self.get_R(False)
        origin_mat[0, :] = 0

        mismatch = self.data.get_mismatch()
        mismatch_matrix = []
        mat = []
        for i in range(len(self.image_cluster_list)):
            v = origin_mat[:, np.array(self.image_cluster_list[i]["cluster_idxs"])]
            v = v.sum(axis=1)
            m = mismatch[np.array(self.image_ids_of_clusters[i])].sum(axis=0)
            mismatch_matrix.append(m)
            mat.append(v)
        # descendants = self.text_tree_helper\
        #     .get_all_leaf_descendants(self.text_tree_helper.tree)
        # text_labels = [d["id"] for d in descendants[::-1]]
        mismatch_matrix = np.array(mismatch_matrix)
        mat = np.array(mat).T
        for idx, m in enumerate(mat):
            v = (m > m.mean() * 2).astype(int)
            mat[idx] = v

        return mat.T, mismatch_matrix

    def get_current_hypergraph(self):
        cam_matrix, mismatch = self.get_cluster_association_matrix()
        self.data.get_precision_and_recall()
        self.text_tree_helper.assign_precision_and_recall(\
            self.data.precision, self.data.recall)
        self.text_tree_helper.assign_mismatch(mismatch)

        # reordering
        leaf_nodes = self.text_tree_helper.get_all_leaf_descendants(self.text_tree_helper.tree)
        leaf_nodes = leaf_nodes[::-1]
        pos = []
        for i in range(cam_matrix.shape[0]):
            p = 0
            count = 0 
            for j in range(len(leaf_nodes)):
                idx = leaf_nodes[j]["id"]
                if cam_matrix[i][idx] > 0:
                    p = p + j
                    count += 1
            pos.append(p/count)
        sorted_idxs = np.array(pos).argsort()
        cam_matrix = cam_matrix[sorted_idxs, :]
        mismatch = mismatch[sorted_idxs, :]

        mat = {
            "text_tree": self.text_tree,
            "image_cluster_list": [self.image_cluster_list[i] for i in sorted_idxs],
            "mismatch": mismatch.tolist(),
            "cluster_association_matrix": cam_matrix.tolist(),
            "vis_image_per_cluster": {i: self.get_rank(i) for i in range(len(self.image_cluster_list))}
        }
        return mat

    def get_kmeans_by_image_cluster_id(self, image_cluster_id, k=10):
        kmeans_res_dir = os.path.join(self.data_root, "kmeans_res")
        check_dir(kmeans_res_dir)
        filepath = os.path.join(kmeans_res_dir, str(image_cluster_id) + ".pkl")
        if os.path.exists(filepath):
            labels = pickle_load_data(filepath)
            return labels
        image_ids = self.image_ids_of_clusters[image_cluster_id]
        features = self.data.get_image_feature()[np.array(image_ids)]
        print("features.shape", features.shape)
        norm = (features**2).sum(axis=1)
        norm = norm ** 0.5
        norm_features = features / norm.reshape(-1,1)

        pred = self.data.get_category_pred(image_ids, "image")
        norm = (pred**2).sum(axis=1)
        norm = norm ** 0.5
        norm_pred = pred / (norm.reshape(-1,1)+1e-12)
        cluster_feature = np.concatenate((norm_features, norm_pred), axis=1)

        labels = self._kmeans(cluster_feature, k)
        pickle_save_data(filepath, labels)
        return labels


    def get_rank(self, image_cluster_id):
        rank_res_path = os.path.join(self.data_root, "rank_res.json")
        if str(image_cluster_id) in self.rank_res \
            and self.rank_res[str(image_cluster_id)] is not None:
            top_k = self.rank_res[str(image_cluster_id)]
        elif os.path.exists(rank_res_path):
            logger.info("loading rank result from buffer")
            self.rank_res = json_load_data(rank_res_path)
            top_k = self.rank_res[str(image_cluster_id)]
        else:
            image_ids = self.image_ids_of_clusters[image_cluster_id]
            mismatch = self.data.get_mismatch()[np.array(image_ids)].sum(axis=1)
            confidence = self.data.get_mean_confidence()[np.array(image_ids)]
            total_score = mismatch #- confidence * 100
            total_score = np.random.rand(len(total_score))
            np.random.seed(124)
            top_k = []
            k = 10
            labels = self.get_kmeans_by_image_cluster_id(image_cluster_id, k)
            for i in range(k):
                idxs = np.array(range(len(labels)))[labels==i]
                score = total_score[idxs]
                top_k.append(image_ids[idxs[score.argmax()]])
            # sorted_idxs = total_score.argsort()[::-1]
            # top_k = [image_ids[i] for i in sorted_idxs[:13]]
            self.rank_res[str(image_cluster_id)] = top_k
        res = [self.data.get_detection_result_for_vis(i) for i in top_k]
        return res

    def get_tsne_of_image_cluster(self, image_cluster_id):
        tsne_root = os.path.join(self.data_root, "tsne_of_image_cluster")
        check_dir(tsne_root)
        tsne_path = os.path.join(tsne_root, str(image_cluster_id) + ".pkl")
        if os.path.exists(tsne_path):
            logger.info("tsne buffer of image cluster {} exists".format(image_cluster_id))
            return pickle_load_data(tsne_path)
        logger.info("TSNE buffer did not exists, run TSNE")
        image_ids = self.image_ids_of_clusters[image_cluster_id]
        features = self.data.get_image_feature()[np.array(image_ids)]
        print("features.shape", features.shape)
        norm = (features**2).sum(axis=1)
        norm = norm ** 0.5
        norm_features = features / norm.reshape(-1,1)

        pred = self.data.get_category_pred(image_ids, "image")
        norm = (pred**2).sum(axis=1)
        norm = norm ** 0.5
        norm_pred = pred / (norm.reshape(-1,1)+1e-12)
        cluster_feature = np.concatenate((norm_features, norm_pred), axis=1)
        # cluster_feature = norm_features

        tsne = TSNE(n_components=2,random_state=15)
        coor = tsne.fit_transform(cluster_feature)
        pickle_save_data(tsne_path, coor)
        logger.info("finish TSNE")
        return coor

    def get_word(self, query):
        tree_node_ids = query["tree_node_ids"]
        match_type = query["match_type"]
        # TODO we should compute the intersection for text examples instead of keywords extract from them
        count = {}
        for tree_node_id in tree_node_ids:
            node = self.text_tree_helper.get_node_by_tree_node_id(tree_node_id)
            leaf_node = self.text_tree_helper.get_all_leaf_descendants(node)
            cats = [n["cat_id"] for n in leaf_node]
            words = self.data.get_word(cats, match_type)
            print(tree_node_id, words)
            for word in words:
                if word[0] not in count:
                    count[word[0]] = []
                count[word[0]].append(word[1])
        union_words = []
        for word in count:
            # if len(count[word]) == len(tree_node_ids):
            union_words.append([word, sum(count[word])])
        print('union:', union_words)
        return union_words

    def get_grid_layout(self, left_x, top_y, width, height, node_id):
        # node_id for navigation 
        return self.current_sampler.get_grid_layout(left_x, top_y, \
            width, height, node_id)

    def set_focus_image_cluster(self, id):
        # self.current_sampler = self.samples[id]
        if hasattr(self, "current_sampler") and \
            self.current_sampler.id == id:
            return 
        self.current_sampler = Sampler(id=id)
        image_ids = self.image_ids_of_clusters[id]
        mismatch = self.data.get_mismatch()
        mismatch = mismatch[np.array(image_ids)]
        self.current_sampler.init(self.get_tsne_of_image_cluster(id),
            image_ids, mismatch, self.data_all_step_root)
        

    def save_model(self, path=None):
        logger.info("save model buffer")
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
        logger.info(buffer_path)
        if os.path.exists(buffer_path):
            return True
        else:
            return False
    
    