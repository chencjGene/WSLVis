import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from flask import send_file
from .utils.config_utils import config
import json
import time

from .port_utils import get_image, get_origin_image, get_image_ids_by_prediction, get_image_box_by_image_id


image = Blueprint("image", __name__)

@image.route("/image/image", methods=["GET"])
def app_get_image():
    idx = request.args["filename"].split(".")[0]
    idx = int(idx)
    img_path = get_image(idx)
    return send_file(img_path)

@image.route("/text/GetImage", methods=["GET", "POST"])
def app_get_image_ids():
    query_data = json.loads(request.data)["query"]
    return get_image_ids_by_prediction(query_data)

@image.route("/text/GetImageBox", methods=["GET", "POST"])
def app_get_image_box():
    image_id = json.loads(request.data)["image_id"]
    return get_image_box_by_image_id(image_id)


@image.route("/image/origin_image", methods=["GET"])
def app_get_origin_image():
    idx = request.args["filename"].split(".")[0]
    idx = int(idx)
    img_path = get_origin_image(idx)
    return send_file(img_path)

@image.route("/image/SingleImageDetection", methods=["GET", "POST"])
def app_get_single_image_detection():
    idx = json.loads(request.data)["image_id"]
    conf = json.loads(request.data).get("conf", None)
    idx = int(idx)
    res = get_image_detection(idx, conf)
    return res