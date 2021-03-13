import os
import numpy as np
import scipy.io as sio
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
from .utils.helper_utils import pickle_load_data
import json
import time
from sklearn.manifold import TSNE, MDS
from sklearn.cluster import KMeans, MiniBatchKMeans, DBSCAN
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics import pairwise_distances

from .port_utils import *


detection = Blueprint("detection", __name__)

@detection.route("/detection/GetManifest", methods=["GET", "POST"])
def app_get_manifest():
    # extract info from request
    dataname = json.loads(request.data)["dataset"]
    step = json.loads(request.data)["step"]
    init_model(dataname, step)
    return get_manifest()
    
@detection.route("/detection/HyperGraph", methods=["GET", "POST"])
def app_get_hypergraph():
    return get_current_hypergraph()

@detection.route("/detection/Rank", methods=["GET", "POST"])
def app_get_rank():
    image_cluster_id = json.loads(request.data)
    return get_rank(image_cluster_id)

@detection.route("/detection/GridLayout", methods=["GET", "POST"])
def app_get_grid_layout():
    data = json.loads(request.data)
    image_cluster_id = data.get("image_cluster_id", 4)
    left_x = data.get("left-x", 0)
    top_y = data.get("top-y", 0)
    width = data.get("width", 1)
    height = data.get("height", 1)
    node_id = data.get("node-id", -1)
    print("image_cluster_id: {}, right_x {}, "
                "top_y {}, width {}, height {}, node id: {}"
                .format(image_cluster_id, left_x, top_y, width, height, node_id))
    return get_grid_layout(image_cluster_id, left_x, top_y, width, height, node_id)


# for debug
@detection.route("/detection/Embedding", methods=["GET", "POST"])
def app_get_embedding():
    port = init_model("COCO17", "step1")
    m = port.model
    m = pickle_load_data(m.buffer_path)
    m.dataname = "COCO20"
    m._init_data()
    cluster_id = 8
    image_ids = m.image_ids_of_clusters[cluster_id]
    image_labels = m.data.get_category_pred(label_type="all", \
        data_type="image", threshold=0.2)
    text_labels = m.data.get_category_pred(label_type="all", data_type="text")
    mismatch = (image_labels!=text_labels)[np.array(image_ids)][:, 59]
    # mismatch = m.data.get_mismatch()[np.array(image_ids)][:, 59]
    mismatch = mismatch.astype(int)
 
    # pd = pairwise_distances(features)
    # outlier_degree = []
    # for i in range(len(labels)):
    #     d = pd[i]
    #     selected_idxs = d.argsort()[:10]
    #     selected_labels = labels[selected_idxs]
    #     outlier_degree.append(sum(selected_labels != labels[i]))
    # outlier_degree = np.array(outlier_degree)
    # labels[outlier_degree > 5] = 1
    # labels[outlier_degree <= 5] = -1

    coor = m.get_tsne_of_image_cluster(cluster_id)
    print("tsne shape", coor.shape)

    coor = coor - coor.min(axis=0).reshape(1,2)
    coor = coor / coor.max(axis=0).reshape(1,2)
    coor = [[int(round(j, 3)* 1000) for j in i] for i in coor]

    data = []
    # for i in range(100):
    for i in range(len(image_ids)):
        data.append({
            "id": image_ids[i],
            "idx": i,
            "c": int(mismatch[i]),
            "p": coor[i]
        })
    # return jsonify(features)
    # return jsonify(features[:100])
    return jsonify(data)
