import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
import json
import time

from .model_utils import *

hybrid = Blueprint("hybrid", __name__)

@hybrid.route("/hybrid/GetManifest", methods=["GET", "POST"])
def app_get_manifest():
    # extract info from request
    dataname = json.loads(request.data)["dataset"]
    init_model(dataname)
    return get_manifest()
    
@hybrid.route("/hybrid/HyperGraph", methods=["GET", "POST"])
def app_get_hypergraph():
    return get_current_hypergraph()