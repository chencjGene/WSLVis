import os
from flask import abort, session
from flask import render_template, jsonify
from flask import Blueprint, request
from .utils.config_utils import config
import json
import time


text = Blueprint("text", __name__)

