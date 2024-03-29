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
    label_consistency = json.loads(request.data).get("label_consistency", None)
    symmetrical_consistency = json.loads(request.data).get("symmetrical_consistency", None)
    # next_step = False
    if label_consistency is not None and symmetrical_consistency is not None:
        step += 1
    else:
        step = None
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
    t = time.time()
    data = json.loads(request.data)
    image_cluster_id = data.get("image_cluster_id", 4)
    cat_ids = data.get("cat_ids", [7])
    if len(cat_ids) == 0:
        cat_ids = [7]
    left_x = data.get("left-x", 0)
    top_y = data.get("top-y", 0)
    width = data.get("width", 1)
    height = data.get("height", 1)
    node_id = data.get("node-id", -1)
    print("image_cluster_id: {}, right_x {}, "
                "top_y {}, width {}, height {}, node id: {}"
                .format(image_cluster_id, left_x, top_y, width, height, node_id))
    print("cat_ids", cat_ids)
    grid_layout = get_grid_layout(image_cluster_id, cat_ids, left_x, top_y, width, height, node_id)
    
    return grid_layout


# for debug
@detection.route("/detection/Embedding", methods=["GET", "POST"])
def app_get_embedding():
    port = init_model("COCO17", "step3")
    m = port.model
    m.update_hiera("sub1")
    m.run()
    cluster_id = 3
    class_id = 7
    image_ids = m.image_ids_of_clusters[cluster_id]
    image_labels = m.data.get_category_pred(label_type="all", \
        data_type="image", threshold=0.5)
    text_labels = m.data.get_category_pred(label_type="all", data_type="text-only")
    gt = m.data.get_groundtruth_labels(label_type="all")
    mismatch = (image_labels!=text_labels)[np.array(image_ids)][:, class_id]
    selected_img = image_labels[np.array(image_ids)][:,class_id]
    selected_text = text_labels[np.array(image_ids)][:,class_id]
    selected_gt = gt[np.array(image_ids)][:,class_id]

    mismatch = mismatch.astype(int)
    # for i, id in enumerate(image_ids):
    #     if mismatch[i]:
    #         if selected_img[i] != selected_gt[i] and selected_img[i] == 1:
    #             mismatch[i] = 3
    #         elif selected_img[i] != selected_gt[i] and selected_img[i] == 0:
    #             mismatch[i] = 4
    #         elif selected_text[i] != selected_gt[i] and selected_text[i] == 0:
    #             mismatch[i] = 2

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
            "img": selected_img[i],
            "text": selected_text[i],
            "p": coor[i]
        })
    # return jsonify(features)
    # return jsonify(features[:100])
    return jsonify(data)
