import os
import numpy as np
import sys
from tqdm import tqdm
from time import time
import argparse
import sqlite3
import json
from flask import jsonify
from application.views.database_utils.data import Data
from application.views.utils.config_utils import config
from application.views.utils.helper_utils import json_load_data, json_save_data
from application.views.utils.helper_utils import pickle_load_data, pickle_save_data


parser = argparse.ArgumentParser(
    description='test')
train_set = parser.add_mutually_exclusive_group()
parser.add_argument('--step', default='',
                    type=str, help='main or debug')
parser.add_argument('--dataname', default='COCO17',
                    type=str, help='main or debug')
args = parser.parse_args()
if len(args.step) == 0:
    raise ValueError("args.step should be specified")


def convert(dataname):
    data = Data(dataname, args.step)
    database_file = os.path.join(data.data_root, "database.db")
    print("database_file", database_file)

    if os.path.exists(database_file):
        os.remove(database_file)
    
    conn = sqlite3.connect(database_file)
    
    conn.execute('''create table annos
    (id int primary key not null,
    cap text not null,
    bbox text not null,
    logits text not null,
    labels text not null,
    activations text not null,
    string text not null,
    image_output text not null,
    detection text not null
    );
    ''')
    conn.execute("create index index_id on annos (id);")
    conn.commit()


    c = conn.cursor()
    sql = "insert into annos (id, cap, bbox, logits, labels, activations, string, image_output, detection) values(?,?,?,?,?,?,?,?,?)"


    # annos = []
    # for a in tqdm(data.annos):
    #     bbox = a["bbox"]
    #     annos += bbox
    # annos = np.array(annos)
    # np.save(os.path.join(data.data_root, "annos.npy"), annos)

    # caps = []
    # bboxs = []
    # logits = []
    # labels = []
    # activations = []
    add_annos = pickle_load_data("test/detection/add_annos_merge.pkl")

    results = []
    for idx in tqdm(range(len(data.annos))):
        anno = data.annos[idx]
        cap = anno["caption"]
        cap = [a+ " " for a in cap]
        cap = "".join(cap)
        bbox = json.dumps(anno["bbox"])
        label = json.dumps(np.round(anno["extracted_labels"]["label"], 4).tolist())
        activation = json.dumps(anno["extracted_labels"]["activations"])
        string = json.dumps(anno["extracted_labels"]["string"])
        image_output = json.dumps(np.round(anno["extracted_labels"]["output_v"], 4).tolist())
        logit = anno["extracted_labels"]["logits"]
        det_cats = [d for d in data.detections[idx]["bbox"] if d[-2] > 0.5]
        image_long_id = data.ids[idx]
        if image_long_id in add_annos.keys() and len(add_annos[image_long_id]["image"]) > 0:
            logit = np.ones(65) * -1
            for d in det_cats:
                logit[d[-1]] = 1
            logit = logit.tolist()
        logit = json.dumps(logit)
        detection = json.dumps(data.detections[idx]["bbox"])
        results.append((idx, cap, bbox, logit, label, activation, string, image_output, detection))

    # caps = np.array(caps)
    # np.save(os.path.join(data.data_root, "caps.npy"), caps)
    c.executemany(sql, results)
    conn.commit()
    conn.close()

    # t0 = time()
    # np.load(os.path.join(data.data_root, "annos.npy"))
    # print("time cost", time() - t0)

def test():
    data_root = os.path.join(config.data_root, config.coco17)
    database_file = os.path.join(data_root, "database.db")
    conn = sqlite3.connect(database_file)

    t0 = time()
    cursor = conn.cursor()
    cursor.execute("select * from annos where id < 1000")
    result = cursor.fetchall()
    a = []
    for a in result:
        idx, cap, bbox, logit, label, activation = a
        bbox = json.loads(bbox)
        logit = json.loads(logit)
        label = json.loads(label)
        activation = json.loads(activation)
    print("time cost", time() - t0)
    # print(result)

def speed_test():
    t0 = time()
    datapath = os.path.join(config.data_root, config.coco17, "debug_processed_data.pkl")
    a = json_load_data(datapath)
    print("time cost", time() - t0)

if __name__ == "__main__":
    convert(args.dataname)
    # test()
    # speed_test()