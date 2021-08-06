# import pickle
import _pickle as pickle
import numpy as np
import os
import cv2
import threading
import sys
import ujson as json
from sklearn.metrics import confusion_matrix, roc_auc_score, \
    precision_recall_curve, auc, roc_curve
from sklearn.preprocessing import OneHotEncoder

from threading import Thread
from time import sleep

exec_list = {}

# Pickle loading and saving
def pickle_save_data(filename, data):
    try:
        pickle.dump(data, open(filename, "wb"))
    except Exception as e:
        print(e, end=" ")
        print("So we use the highest protocol.")
        pickle.dump(data, open(filename, "wb"), protocol=4)
    return True


def pickle_load_data(filename):
    try:
        mat = pickle.load(open(filename, "rb"))
    except Exception:
        mat = pickle.load(open(filename, "rb"))
    return mat


# json loading and saving
def json_save_data(filename, data):
    with open(filename, "w") as f:
        f.write(json.dumps(data))
    return True


def json_load_data(filename, encoding=None):
    with open(filename, "r", encoding=encoding) as f:
        return json.load(f)


# directory
def check_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return True


def check_exist(filename):
    return os.path.exists(filename)


# normalization
def unit_norm_for_each_col(X):
    X -= X.min(axis=0)
    X /= X.max(axis=0)
    return X


def sigmoid(x):
    return 1/(1 + np.exp(-x))

def one_hot_encoder(List):
    res = np.zeros((len(List), max(List) + 1))
    res[np.array(range(len(List))), List] = 1
    return res



# metrics
def accuracy(y_true, y_pred, weights=None):
    score = (y_true == y_pred)
    return np.average(score, weights=weights)


# detection helpers
def area(box):
    xmin, ymin, xmax, ymax = box
    x_len = np.maximum(xmax - xmin, 0.0)
    y_len = np.maximum(ymax - ymin, 0.0)
    area = x_len * y_len
    return area

def intersect(box1, box2):
    xmin1, ymin1, xmax1, ymax1 = box1
    xmin2, ymin2, xmax2, ymax2 = box2
    ymin = np.maximum(ymin1, ymin2)
    xmin = np.maximum(xmin1, xmin2)
    ymax = np.minimum(ymax1, ymax2)
    xmax = np.minimum(xmax1, xmax2)
    box = np.stack([ymin, xmin, ymax, xmax], axis=-1)
    return box

def cal_iou(box1, box2):
    inter = area(intersect(box1, box2))
    union = area(box1) + area(box2) - inter
    iou_v = inter / union
    return iou_v

def draw_box(input_path, boxes):
    # boxes in shape [num_box, 6]
    boxes = np.array(boxes)
    if len(boxes.shape) < 2:
        boxes = boxes.reshape(1, -1)
    boxes_value = boxes[:, :4].astype(float)
    confs = boxes[:, 4]
    cat_names = boxes[:, 5]
    img = cv2.imread(input_path)
    boxes_value = boxes_value.astype(np.int64)
    img = np.array(img, np.float32)
    img = np.array(img*255/np.max(img), np.uint8)
    for i, box in enumerate(boxes_value):
        xmin, ymin, xmax, ymax = box
        conf = confs[i]
        category_name = cat_names[i]
        cv2.rectangle(img,(xmin, ymin),(xmax, ymax), (0, 0, 255), 2)
        cv2.putText(img,
                    category_name+": "+str(conf),
                    (xmin, max(ymin-5, 0)),
                    cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), thickness=1)
    return img

def draw_box_cv(input_path, output_path, boxes):
    # boxes in shape [num_box, 6]
    img = draw_box(input_path, boxes)
    cv2.imwrite(output_path, img)