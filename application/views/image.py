import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from flask import send_file
from .utils.config_utils import config
import json
import time

from .model_utils import get_image

image = Blueprint("image", __name__)

@image.route("/image/image", methods=["GET"])
def app_get_image():
    idx = request.args["filename"].split(".")[0]
    idx = int(idx)
    img_path = get_image(idx)
    return send_file(img_path)
