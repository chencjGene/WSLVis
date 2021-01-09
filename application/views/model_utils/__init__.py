from flask import jsonify
from .model import MMModel

model = MMModel()

def get_manifest():
    #TODO: 
    manifest = {"image_num": 1}
    return jsonify(manifest)

def init_model(dataname):
    model.init(dataname)

def get_current_hypergraph():
    # tree = model.get_tree()
    # set_list = model.get_type()
    tree, set_list = model.data.get_hypergraph()
    mat = {
        "tree": tree,
        "set_list": set_list
    }
    # import IPython; IPython.embed(); exit()
    return jsonify(mat)


def get_image(idx):
    None

def get_text(query):
    text_result = model.data.get_text(query)
    return jsonify(text_result)

def get_word(query):
    return jsonify(model.data.get_word(query))