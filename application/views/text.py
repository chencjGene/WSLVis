import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
import json
import time

from .port_utils import get_text, get_word, get_text_by_word, get_single_text

text = Blueprint("text", __name__)

@text.route("/text/GetWord", methods=["GET", "POST"])
def app_get_word():
    query_data = json.loads(request.data)["query"]
    # query_data = {
    #     "tree_node_id": 1,
    #     "type": "tp"
    # }
    return get_word(query_data)

@text.route("/text/GetText", methods=["GET", "POST"])
def app_get_text():
    query_data = json.loads(request.data)["query"]
    # print(query_data)
    return get_text(query_data)

@text.route("/text/GetTextByWord", methods=["GET", "POST"])
def app_get_text_by_word():
    query_data = json.loads(request.data)["query"]
    # print(query_data)
    return get_text_by_word(query_data)

@text.route("/text/text", methods=["GET"])
def app_get_single_text():
    idx = request.args["filename"].split(".")[0]
    idx = int(idx)
    return get_single_text(idx)