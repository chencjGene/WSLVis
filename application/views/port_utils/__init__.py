from flask import jsonify
from .port import Port

port = Port()

def get_manifest():
    # manifest = {"image_num": 1}
    manifest = port.get_manifest()
    return jsonify(manifest)

def init_model(dataname, step):
    port.reset(dataname, step)

def get_current_hypergraph():
    port.run_model()
    # return jsonify({"test": 1})
    hypergraph = port.get_current_hypergraph()
    # import IPython; IPython.embed(); exit()
    return jsonify(hypergraph)


def get_image(idx):
    return port.model.data.get_image(idx)

def get_text(query):
    text_result = port.model.data.get_text(query)
    return jsonify(text_result)

def get_word(query):
    return jsonify(port.model.data.get_word(query))