import os
import numpy as np
import scipy.io as sio
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
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

# for debug
@detection.route("/detection/Embedding", methods=["GET", "POST"])
def app_get_embedding():
    port = init_model("COCO17", "step1")
    m = port.model
    m.run()
    image_ids = m.image_ids_of_clusters[4]
    features = m.data.get_image_feature()[np.array(image_ids)]
    print("features.shape", features.shape)
    norm = (features**2).sum(axis=1)
    norm = norm ** 0.5
    norm_features = features / norm.reshape(-1,1)

    pred = m.data.get_category_pred(image_ids, "image")
    norm = (pred**2).sum(axis=1)
    norm = norm ** 0.5
    norm_pred = pred / (norm.reshape(-1,1)+1e-12)

    cluster_feature = np.concatenate((norm_features, norm_pred), axis=1)
    print("cluster_feature", cluster_feature.shape)

    labels = m._kmeans(cluster_feature, 7)

    # pd = pairwise_distances(features)
    # outlier_degree = []
    # for i in range(len(labels)):
    #     d = pd[i]
    #     selected_idxs = d.argsort()[:10]
    #     selected_labels = labels[selected_idxs]
    #     outlier_degree.append(sum(selected_labels != labels[i]))
    # outlier_degree = np.array(outlier_degree)
    # labels[outlier_degree > 5] = 1
    # labels[outlier_degree <= 5] =-1

    coor = m.get_tsne_of_image_cluster(4)
    print("tsne shape", coor.shape)

    coor = coor - coor.min(axis=0).reshape(1,2)
    coor = coor / coor.max(axis=0).reshape(1,2)
    coor = [[int(round(j, 3)* 1000) for j in i] for i in coor]

    data = []
    # for i in range(100):
    for i in range(len(features)):
        data.append({
            "id": image_ids[i],
            "idx": i,
            "c": int(labels[i]),
            "p": coor[i]
        })
    # return jsonify(features)
    # return jsonify(features[:100])
    return jsonify(data)
