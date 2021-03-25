# --coding:utf-8 --
import numpy as np
import sys
import os
import cffi
import threading
import time
from sklearn.neighbors import BallTree
import math
from anytree import Node

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import check_dir, pickle_load_data, pickle_save_data

from .gridlayout import grid_layout

from annoy import AnnoyIndex

SO_PATH = os.path.join(config.dll_root)

class Sampler(object):
    def __init__(self, sampling_square_len=45, id=None):
        t = time.time()
        sampling_num = sampling_square_len * sampling_square_len
        self.sampling_square_len = sampling_square_len
        self.sampling_num = sampling_num
        self.id = id

        self.min_adding_len = 0.05
        self.current_count = 1
        logger.info("time cost before self._init {}".format(time.time() - t))


    def init(self, embed_X, image_ids, mismatch, data_root):
        self.data_root = data_root
        self.image_ids = image_ids
        self.train_idx = np.array(range(len(image_ids)))
        self.embed_X = embed_X
        self.mismatch = mismatch.astype(int).mean(axis=1)
        self.train_tree = None
        self.train_tree_data = {}
        self.train_focus_node = None
        self.current_tree = self.train_tree
        self.current_tree_data = self.train_tree_data
        # self.current_count = 1
        self._preprocess()

        self.current_sampled_idx = None
        self.current_sampled_X = None
        self.current_grid_layout = None
        logger.info("finish init")


    def set_class_selection(self):
        None


    def process_idx(self, idx):
        # print("process_idx", idx)
        t = time.time()
        X = self.embed_X[np.array(idx)]
        mismatch = self.mismatch[np.array(idx)] 
        if len(idx) < self.sampling_num:
            sampled_idx = idx
            unsampled_idx = []
            sampled_X = X
        else:
            # sampler = DensityBasedSampler(n_samples=self.sampling_num)
            # res = sampler.fit_sample(X, confidence=confidence, entropy=entropy)
            res = [0]
            res[0] = np.zeros(len(idx)).astype(bool)
            res[0][:self.sampling_num] = True
            sampled_idx = np.array(idx)[res[0]]
            sampled_X = X[res[0]]
            unsampled_idx = np.array(idx)[np.array(1-res[0]).astype(bool)]
        # grid_x = grid_layout(sampled_X)[0]
        print("process_idx. total idx: {}, sampled idx: {}, unsampled idx: {}".format(len(idx),
                                                                         len(sampled_idx),
                                                                         len(unsampled_idx)))
        grid_x = np.ones(sampled_X.shape) * 0.5
        hiera = {}
        for idx, id in enumerate(sampled_idx):
            try:
                hiera[id] = {}
                hiera[id]["g"] = grid_x[idx]
                hiera[id]["c"] = []
            except Exception as e:
                print(e)


        for idx, id in enumerate(unsampled_idx):
            # x = self.data.embed_X[id]
            # dis = ((sampled_X - x) ** 2).sum(axis=1)
            # parent_id = sampled_idx[dis.argmin()]
            hiera[sampled_idx[0]]["c"].append(id)

        # check hiera
        count = 0
        for i in hiera:
            count = count + len(hiera[i]["c"]) + 1
        print("tree_process. hiera total num {}, time cost: {}".format( count, time.time() - t))

        return idx, sampled_idx, grid_x, hiera

    def tree_process(self, idx):
        idx, sampled_idx, grid_x, hiera = self.process_idx(idx)

        tree = Node("root")
        focus_node = tree
        tree_data = {}
        tree_data[focus_node.name] = {
            "instance_idx": idx,
            "sampled_idx": sampled_idx,
            "grid_layout": grid_x,
            "hiera": hiera,
            "node": tree,
        }
        return tree, focus_node, tree_data

    def _preprocess(self):
        # training hierarchical process
        self.train_tree, self.train_focus_node, self.train_tree_data = \
            self.tree_process(self.train_idx)


    def get_grid_layout(self, left_x, top_y, width, height, node_id):
        t = time.time()
        self.current_tree = self.train_tree
        self.current_tree_data = self.train_tree_data
        if node_id < 0:
            node_id = "root"
            left_x = 0
            top_y = 0
            width = height = 1
            print("using root")
        else:
            node_id = "id-" + str(node_id)
        self.current_focus_node = self.current_tree_data[node_id]["node"]
        node_data = self.current_tree_data[self.current_focus_node.name]
        current_hiera = node_data["hiera"]

        # check hiera
        count = 0
        for i in current_hiera:
            count = count + len(current_hiera[i]["c"]) + 1
        print("hiera total num",count)

        selected_list = []
        selected_pos = []
        for id in current_hiera:
            x = current_hiera[id]["g"][0]
            y = current_hiera[id]["g"][1]
            if (x > left_x and x < (left_x + width)) and \
                    (y > top_y and y < (top_y + height)):
                selected_list.append(id)
                selected_pos.append([(x - left_x) / width, (y - top_y)/height])
        idx, sampled_idx, grid_x, hiera, sampling_res = \
            self._get_sampler(selected_list, selected_pos, current_hiera, node_id)
        new_node = Node("id-" + str(self.current_count), parent=self.current_focus_node)
        self.current_count = self.current_count + 1
        self.current_focus_node = new_node
        self.current_tree_data[self.current_focus_node.name] = {
            "instance_idx": idx,
            "sampled_idx": sampled_idx,
            "grid_layout": grid_x,
            "hiera": hiera,
            "node": new_node,
        }
        print("self.get_sampler grid layout and sampler time cost:", time.time() - t)
        return {
            "id": self.current_count - 1,
            "layout": sampling_res,
        }

    def _get_sampler(self, selected_list, selected_pos, current_hiera, old_node_id):
        idx = []
        print("selected idx len", len(selected_list))
        for id in selected_list:
            idx.extend(current_hiera[id]["c"] + [id])

        print("all idx len:", len(idx))
        print("selected list", selected_list)


        # 特殊处理 for the first time
        if old_node_id == "root":
            selected_list = []
            selected_pos = []
            
        check_dir(os.path.join(self.data_root, "heirarchy"))
        buffer_path = os.path.join(self.data_root, "heirarchy", "heira_" + str(self.id) + ".pkl")

        if os.path.exists(buffer_path) and old_node_id == "root":
            logger.info("using hiera buffer!!!")
            idx, sampled_idx, self.current_grid_layout, hiera, res = pickle_load_data(buffer_path)
            self.current_sampled_idx = sampled_idx
            grid_x = self.current_grid_layout[0]

        else:
            X = self.embed_X[np.array(idx)]
            mismatch = self.mismatch[np.array(idx)]
            if len(idx) < self.sampling_num:
                sampled_idx = np.array(idx)
                sampled_X = X
                unsampled_idx = []
            else:
                print("total instances needed to sampled: ", len(idx))
                intersection_idx = list(set(idx).intersection(set(selected_list)))
                selection = np.zeros(len(idx), dtype=bool)
                for id in intersection_idx:
                    selection[idx.index(id)] = True
                sampler = DensityBasedSampler(n_samples=self.sampling_num)
                res = sampler.fit_sample(X, mismatch=mismatch, selection=np.array(selection))
                sampled_idx = np.array(idx)[res[0]]
                print("sampled idx",sampled_idx)
                sampled_X = X[res[0], :]
                unsampled_idx = np.array(idx)[np.array(1-res[0]).astype(bool)]
            self.current_sampled_idx = sampled_idx
            self.current_history_idx = sampled_idx.copy()
            self.current_sampled_x = sampled_X
            test_sampled_X = sampled_X.copy()
            self.current_grid_layout = grid_layout(sampled_idx, sampled_X,
                selected_list, selected_pos, self.mismatch)
            res = []
            grid_x = self.current_grid_layout[0]

            hiera = {}
            for idx, id in enumerate(sampled_idx):
                hiera[id] = {}
                hiera[id]["g"] = grid_x[idx]
                hiera[id]["c"] = []

            for idx, id in enumerate(unsampled_idx):
                x = self.embed_X[id]
                dis = ((sampled_X - x) ** 2).sum(axis=1)
                parent_id = sampled_idx[dis.argmin()]
                hiera[parent_id]["c"].append(id)

            for idx, id in enumerate(sampled_idx):
                res.append({
                    'id': int(id),
                    'img_id': self.image_ids[int(id)],
                    'pos': grid_x[idx].tolist(),
                    'mismatch': self.mismatch[int(id)]
                })
            if old_node_id == "root":
                pickle_save_data(buffer_path, [idx, sampled_idx, self.current_grid_layout, hiera, res])

        return idx, sampled_idx, grid_x, hiera, res

def Knn(X1, N, D, n_neighbors, forest_size, subdivide_variance_size, leaf_number):
    forest = AnnoyIndex(X1.shape[1], 'euclidean')
    forest_size = 10
    indices = []
    distances = []
    for i in range(N):
        forest.add_item(i, X1[i])
    forest.build(forest_size)
        
    for i in range(N):
        ret = forest.get_nns_by_item(i, n_neighbors + 1, include_distances = True)
        indices.append(ret[0][1:])
        distances.append(ret[1][1:])
    indices = np.array(indices)
    distances = np.array(distances)
    return indices, distances


class DensityBasedSampler(object):
    """
    exact density biased sampling:
    under-sample dense regions and over-sample light regions.

    Ref: Palmer et al., Density Biased Sampling: An Improved Method for Data Mining and Clustering ,SIGMOD 2000
    """
    random_state = 42
    n_samples = -1
    N = -1
    tree = "None"
    estimated_density = "None"
    prob = "None"
    alpha = 1

    def __init__(self, n_samples, annFileName="none.ann", alpha=1, beta=1, random_state=0, use_pca=False,
                 pca_dim=50):
        self.n_samples = n_samples
        self.random_state = random_state
        self.alpha = alpha
        self.beta = beta
        assert beta >= 0, 'beta should be non-negative'
        self.use_pca = use_pca
        self.pca_dim = pca_dim
        self.annFileName = annFileName

    def fit_sample(self, data: np.ndarray, label=None, return_others=True, selection=None, mismatch=None):
        if type(data) == list:
            data = np.array(data)

        if self.use_pca:
            data = data - np.mean(data, axis=0)
            cov_x = np.dot(np.transpose(data), data)
            [eig_val, eig_vec] = np.linalg.eig(cov_x)

            # sorting the eigen-values in the descending order
            eig_vec = eig_vec[:, eig_val.argsort()[::-1]]
            initial_dims = self.pca_dim
            if initial_dims > len(eig_vec):
                initial_dims = len(eig_vec)

            # truncating the eigen-vectors matrix to keep the most important vectors
            eig_vec = np.real(eig_vec[:, :initial_dims])
            data = np.dot(data, eig_vec)

        self.N = len(data)
        if self.N <= self.n_samples:
            return [True] * self.N
        # np.random.seed(42)
        selection = self._fit_sample(data, label=label, selection=selection, mismatch=mismatch)
        if return_others:
            return selection, self.estimated_density, self.prob
        else:
            return selection

    def _fit_sample(self, data: np.ndarray, label=None, selection=None, mismatch=None):
        if selection is not None and selection.sum() >= self.n_samples:
            return selection
        knn = 50
        X = np.array(data.tolist(), dtype=np.float64)
        N, D = X.shape
        if knn + 1 > N:
            knn = int((N - 1) / 2)
        neighbor, dist = Knn(X, N, D, knn + 1, 1, 1, int(N))
        self.radius_of_k_neighbor = dist[:, -1]
        M = mismatch.sum()

        knn //= 2
        if knn + 1 > M:
            knn = int((M - 1) / 2)

        X2 = X[mismatch]
        mismatch_index = [i for i in range(len(mismatch)) if mismatch[i]]
        _, mis_dist = Knn(X2, M, D, knn + 1, 1, 1, int(M))
        self.radius_of_k_mis_neighbor = dist[:, -1].copy()
        for i, j in enumerate(mismatch_index):
            self.radius_of_k_mis_neighbor[j] = mis_dist[i, -1]

        for i in range(len(self.radius_of_k_neighbor)):
            self.radius_of_k_neighbor[i] = math.sqrt(self.radius_of_k_neighbor[i])
        maxD = np.max(self.radius_of_k_neighbor)
        minD = np.min(self.radius_of_k_neighbor)
        for i in range(len(self.radius_of_k_neighbor)):
            self.radius_of_k_neighbor[i] = ((self.radius_of_k_neighbor[i] - minD) * 1.0 / (maxD - minD)) * 0.5 + 0.5
            #self.radius_of_k_neighbor[i] = 1


        for i in range(len(self.radius_of_k_mis_neighbor)):
            self.radius_of_k_mis_neighbor[i] = math.sqrt(self.radius_of_k_mis_neighbor[i])
        maxR = np.max(self.radius_of_k_mis_neighbor)
        minR = np.min(self.radius_of_k_mis_neighbor)
        for i in range(len(self.radius_of_k_mis_neighbor)):
            self.radius_of_k_mis_neighbor[i] = ((maxR - self.radius_of_k_mis_neighbor[i]) * 1.0 / (maxR - minR)) ** 3
            if not mismatch[i]:
                self.radius_of_k_mis_neighbor[i] = 1

        self.beta *= 4
        self.prob = (self.radius_of_k_mis_neighbor) * (self.radius_of_k_neighbor + self.beta * (mismatch ** 2)) # 采样概率与r和类标混杂度成正比
        mis_prob = self.prob[mismatch_index]
        for i in range(0, len(mis_prob), 100):
            print(i, mis_prob[i: i + 100])
        self.prob = self.prob / self.prob.sum()
        if selection is None:
            selection = np.zeros(self.N, dtype=bool)
        np.random.seed(self.random_state)
        selected_index = np.random.choice(self.N, self.n_samples,
                                          replace=False, p=self.prob)
        np.random.seed()
        count = selection.sum()
        for i in range(self.N):
            if count >= self.n_samples:
                break
            if not selection[selected_index[i]]:
                count += 1
                selection[selected_index[i]] = True
        return selection



if __name__ == '__main__':
    d = Data(config.dog_cat)
    X_train, y_train, X_valid, y_valid, X_test, y_test = d.get_data("all")
    embed_X_train, embed_X_valid, embed_X_test = d.get_embed_X("all")
    s = DensityBasedSampler(n_samples=20)
    sub = s.fit_sample(X_train)

    print(sub)
