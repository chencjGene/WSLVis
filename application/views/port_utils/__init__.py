from flask import jsonify
from .port import Port
import numpy as np

port = Port()

def get_manifest():
    # manifest = {"image_num": 1}
    manifest = port.get_manifest()
    return jsonify(manifest)

def init_model(dataname, step):
    port.reset(dataname, step)
    return port

def get_current_hypergraph():
    port.run_model()
    # return jsonify({"test": 1})
    hypergraph = port.get_current_hypergraph()
    # import IPython; IPython.embed(); exit()
    return jsonify(hypergraph)

def get_grid_layout(image_cluster_id, cat_ids, left_x, top_y, width, height, node_id):
    port.model.set_focus_image_cluster(image_cluster_id, cat_ids)
    res = port.model.get_grid_layout(left_x, top_y, width, height, node_id, cat_ids)
    return jsonify(res)

def get_rank(image_cluster_id):
    res = port.get_rank(image_cluster_id)
    return jsonify(res)

def get_image(idx):
    return port.model.data.get_image(idx)

def get_origin_image(idx):
    return port.model.data.get_origin_image(idx)

def get_image_detection(img_id, conf=None):
    res = port.model.data.get_detection_result_for_vis(img_id, conf, use_buffer=False)
    return jsonify(res)


def get_single_text(idx):
    text = port.model.data.get_single_text(idx)
    return jsonify(text)

def get_word(query):
    return jsonify(port.model.get_word(query))

def get_text(query):
    text_result = port.model.data.get_text(query)
    return jsonify(text_result)

def get_text_by_word(query):
    text_result = port.model.get_text_by_word(query)
    return jsonify(text_result)


def get_image_ids_by_prediction(query):
    predictions = port.model.data.get_category_pred(label_type="all", data_type="text-only")
    # if port.model.step == 1:
    #     predictions = port.model.data.get_groundtruth_labels(label_type="all")
    selection = np.where(predictions[:,query['tree_node_ids']].sum(axis=1) == len(query['tree_node_ids']))[0]
    max_image_num = 100
    if selection.shape[0] > max_image_num:
        selection = selection[np.random.choice(selection.shape[0], max_image_num, replace=False)]
    res = [port.model.data.get_detection_result_for_vis(int(x)) for x in selection]
    # print(res)
    return jsonify(res)

    