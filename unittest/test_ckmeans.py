import numpy as np
import umap
import matplotlib.pyplot as plt
import unittest
import pickle
import os
import seaborn as sns
from ortools.graph import pywrapgraph

from sklearn.datasets import load_digits
from sklearn.datasets import fetch_openml
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans, MiniBatchKMeans

# from application.views.database_utils.k_means_constrained_ import KMeansConstrained
from application.views.constrained_kmeans.k_means_constrained_ import KMeansConstrained
# from k_means_constrained import KMeansConstrained
from application.views.database_utils import Data
from application.views.database_utils.set_helper import CoClustering
from application.views.database_utils.spectral_biclustering import SpectralBiclustering
from application.views.database_utils.utils import multiclass_precision_and_recall
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import pickle_load_data, one_hot_encoder
from application.views.database_utils.utils import decoding_categories, encoding_categories


class CKMeansTest(unittest.TestCase):
    def test_size_constraint(self):
        # X = np.array([[1, 2], [1, 4], [1, 0],[4, 2], [4, 4], [4, 0]])
        X = np.array([[0, 0], [0, 1], [1, 0],[1, 1], 
            [2, 2], [2, 3]])
        bi_cost = [2, 1, 1, 1, 0, 1]
        clf = KMeansConstrained(
            n_init=1,
            n_clusters=2,
            size_min=1,
            size_max=5,
            random_state=0
        )
        clf.fit_predict(X, bi_cost)
        print(clf.labels_)
        a = 1

    def test_real_data(self):
        kmeans_result = "kmeans-3.npy"
        d = Data(config.coco17, suffix="step1")
        image_labels = d.get_category_pred(label_type="all", data_type="image")
        text_labels = d.get_category_pred(label_type="all", data_type="text")
        mismatch = (image_labels!=text_labels).sum(axis=1)
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
        clf = KMeansConstrained(
            n_init=1,
            n_clusters=100,
            size_min=1,
            size_max=2000,
            random_state=0
        )
        clf.fit_predict(feature, mismatch)
        # print(clf.labels_)
        labels = clf.labels_
        np.save("test/mismatch/constrained-kmeans-3.npy", labels)
        a = 1


    def test_mini_cost_flow(self):
        """MinCostFlow simple interface example."""

        # Define four parallel arrays: start_nodes, end_nodes, capacities, and unit costs
        # between each pair. For instance, the arc from node 0 to node 1 has a
        # capacity of 15 and a unit cost of 4.

        start_nodes = [ 0, 0,  1, 1,  1,  2, 2,  3, 4]
        end_nodes   = [ 1, 2,  2, 3,  4,  3, 4,  4, 2]
        capacities  = [15, 8, 20, 4, 10, 15, 4, 20, 5]
        unit_costs  = [ 4, 4,  2, 2,  6,  1, 3,  2, 3]

        # Define an array of supplies at each node.

        supplies = [20, 0, 0, -5, -15]


        # Instantiate a SimpleMinCostFlow solver.
        min_cost_flow = pywrapgraph.SimpleMinCostFlow()

        # Add each arc.
        for i in range(0, len(start_nodes)):
            min_cost_flow.AddArcWithCapacityAndUnitCost(start_nodes[i], end_nodes[i],
                                                        capacities[i], unit_costs[i])

        # Add node supplies.

        for i in range(0, len(supplies)):
            min_cost_flow.SetNodeSupply(i, supplies[i])


        # Find the minimum cost flow between node 0 and node 4.
        if min_cost_flow.Solve() == min_cost_flow.OPTIMAL:
            print('Minimum cost:', min_cost_flow.OptimalCost())
            print('')
            print('  Arc    Flow / Capacity  Cost')
            for i in range(min_cost_flow.NumArcs()):
                cost = min_cost_flow.Flow(i) * min_cost_flow.UnitCost(i)
                print('%1s -> %1s   %3s  / %3s       %3s' % (
                    min_cost_flow.Tail(i),
                    min_cost_flow.Head(i),
                    min_cost_flow.Flow(i),
                    min_cost_flow.Capacity(i),
                    cost))
        else:
            print('There was an issue with the min cost flow input.')

        a = 1

if __name__ == '__main__':
    unittest.main()