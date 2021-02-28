import os
import numpy as np
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
import json
import time

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
    embedding_path = "test/feature/tsne-embedding.npy"
    init_model("COCO17", "step1")
    features = np.load(embedding_path)
    features = features - features.min(axis=0).reshape(1,2)
    features = features / features.max(axis=0).reshape(1,2)
    features = [[int(round(j, 3)* 1000) for j in i] for i in features]
    labels = np.load("test/feature/kmeans-3.npy")
    # labels = np.load("test/mismatch/max-3000-constrained-kmeans-3.npy")
    print(features[1:3])
    data = []
    # for i in range(100):
    for i in range(len(labels)):
        data.append({
            "id": i,
            "c": int(labels[i]),
            "p": features[i]
        })
    # return jsonify(features)
    # return jsonify(features[:100])
    return jsonify(data)
