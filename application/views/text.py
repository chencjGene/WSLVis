import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
import json
import time

from .model_utils import get_text

text = Blueprint("text", __name__)

@text.route("/text/GetText", methods=["GET", "POST"])
def app_get_text():
    # query_data = json.loads(request.data)
    query_data = {
        "cat_id": 0,
        "word": "person"
    }
    return get_text(query_data)
