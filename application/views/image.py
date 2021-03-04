import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from flask import send_file
from .utils.config_utils import config
import json
import time

from .port_utils import get_image, get_origin_image

image = Blueprint("image", __name__)

@image.route("/image/image", methods=["GET"])
def app_get_image():
    idx = request.args["filename"].split(".")[0]
    idx = int(idx)
    img_path = get_image(idx)
    return send_file(img_path)


@image.route("/image/origin_image", methods=["GET"])
def app_get_origin_image():
    idx = request.args["filename"].split(".")[0]
    idx = int(idx)
    img_path = get_origin_image(idx)
    return send_file(img_path)