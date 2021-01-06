from flask import Flask, jsonify, send_file, session, \
    request, render_template, send_from_directory
from flask_cors import *
from flask_session import Session
from datetime import timedelta
from .views.admin import admin
from .views.history import history
from .views.hybrid import hybrid
from .views.image import image
from .views.text import text

def create_app():
    app = Flask(__name__)
    CORS(app, resources=r'/*')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    Session(app)

    # app.config.from_object("config.DevelopmentConfig")

    app.register_blueprint(admin)
    app.register_blueprint(history)
    app.register_blueprint(hybrid)
    app.register_blueprint(image)
    app.register_blueprint(text)

    # # this kind of manner is somewhere wrong
    # app.config.update(
    #     DEBUG=True,
    #     SERVER_NAME = "0.0.0.0:8000"
    # )

    return app