import numpy as np
import os 
import cv2
import sqlite3
import json
from tqdm import tqdm

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data, sigmoid
from ..utils.helper_utils import draw_box,check_dir
from ..database_utils.utils import decoding_categories, encoding_categories
from ..database_utils.utils import TFIDFTransform, rule_based_processing, get_precision_and_recall
from .set_helper import SetHelper

DEBUG = False

class DataBaseLoader(object):
    def __init__(self, dataname, step=0):
        self.dataname = dataname 
        self.suffix = "step" + str(step)
        self.data_all_step_root = os.path.join(config.data_root, self.dataname)
        self.data_root = os.path.join(config.data_root, self.dataname, self.suffix)
        self.conf_thresh = 0.5

        self.image_features = None
        self.text_features = None

        database_file = os.path.join(self.data_root, "database.db")
        self.conn = sqlite3.connect(database_file, check_same_thread=False)

        self.width_height = json_load_data(os.path.join(self.data_all_step_root, \
            "width_height.json"))

    def database_fetch_by_idx(self, idx, keys):
        # id, cap, bbox, logits, labels, activations, string, detection, image_output
        cursor = self.conn.cursor()
        keys = "".join([k + ", " for k in keys]).strip(", ")
        sql = "select {} from annos where id = ?".format(keys)
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0]
        if len(res) == 1:
            return res[0]
        else:
            return res
    
    def get_detection_result(self, idx):
        cursor = self.conn.cursor()
        sql = "select detection from annos where id = ?"
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0][0]
        res = json.loads(res)
        return res

    def get_anno_bbox_result(self, idx):
        cursor = self.conn.cursor()
        sql = "select bbox from annos where id = ?"
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0][0]
        res = json.loads(res)
        return res
    
    def get_text_feature(self):
        text_feature_path = os.path.join(self.data_root, "word_feature.npy")
        text_feature = np.load(text_feature_path)
        norm = (text_feature**2).sum(axis=1)
        norm = norm ** 0.5
        text_feature = text_feature / norm.reshape(-1,1)
        return text_feature

    def get_image_feature(self):
        logger.info("get_image_feature")
        if self.image_features is not None:
            return self.image_features
        feature_path = os.path.join(self.data_root, "feature_train.npy")
        features = np.load(feature_path)
        print("feature shape", features.shape)
        sizes = [256, 256, 256, 512, 1024, 512]
        split_points = [0]
        sum = 0
        feature_id = 3
        for i in sizes:
            sum = sum + i
            split_points.append(sum)
        print(split_points)
        self.image_features = \
            features[:, split_points[feature_id]: split_points[feature_id+1]]
        return self.image_features

    def get_detection_result_for_vis(self, idx):
        w, h = self.width_height[idx]
        detection = self.get_detection_result(idx)
        detection = np.array(detection)
        conf_detection = detection[detection[:, -2] > self.conf_thresh].astype(np.float32)
        conf_detection[:, 0] /= w
        conf_detection[:, 2] /= w
        conf_detection[:, 1] /= h
        conf_detection[:, 3] /= h
        conf_detection = np.round(conf_detection, 3)
        return {"idx": idx, "w": w, "h": h, "d": conf_detection.tolist()}


class Data(DataBaseLoader):
    def __init__(self, dataname, step=0):
        super(Data, self).__init__(dataname, step)
        self.class_name = []
        self.class_name_encoding = {}
        self.X = [] # contains image level features and patch level features
        self.annos  = [] # contains text, image level labels, boundingboxes and their categories
        self.detection = [] # contains detection results
        self.ids = []

        self.train_idx = []
        self.valid_idx = []
        self.test_idx = []
        self.redundant_idx = []
        # additional information can be store here
        self.add_info = {}
        
        self.mismatch = None
        self.mean_confidence = None

        self._load_data()

    def _load_data(self):
        logger.info("begin loading data from processed data!")
        filename = config.debug_processed_dataname
        processed_data_filename = os.path.join(self.data_all_step_root, \
            filename.format(""))
        processed_data = json_load_data(processed_data_filename)
        logger.info("finishing load!")
        self.processed_data = processed_data
        self.class_name = processed_data[config.class_name]
        self.X = processed_data[config.X_name]
        self.annos = processed_data[config.annos_name]
        self.detections = processed_data[config.detection_name]
        self.ids = processed_data[config.ids_name]
        self.labeled_idx = processed_data["labeled_idx"]
        self.train_idx = processed_data[config.train_idx_name]
        tmp_map = {}
        for idx in self.train_idx:
            tmp_map[idx] = 0
        for idx in self.labeled_idx:
            tmp_map[idx] = 1
        self.unlabeled_idx = [i for i in self.train_idx if not tmp_map[i]]
        self.val_idx = processed_data[config.valid_idx_name]
        self.test_idx = processed_data[config.test_idx_name]
        self.redundant_idx = processed_data[config.redundant_idx_name]
        self.add_info = processed_data[config.add_info_name]

        logger.info("end loading data from processed data!")

    def run(self):
        None

    def get_precision_and_recall(self):
        labels = []
        cursor = self.conn.cursor()
        sql = "select activations, logits, string, labels from annos where id = ?"
        for i in self.labeled_idx:
            cursor.execute(sql, (i,))
            activation, logits, string, label = cursor.fetchall()[0]
            el = {
                "activations": json.loads(activation),
                "string": json.loads(string),
                "logits": json.loads(logits),
                "label": json.loads(label),
            }
            el["rule_logit"] = rule_based_processing(el, self.suffix)
            labels.append(el)
        self.labeled_p, self.precision, self.recall = get_precision_and_recall(labels)

    def get_labeled_id_by_type(self, cats: list, match_type: str) -> list:
        cursor = self.conn.cursor()
        sql = "select labels, logits from annos where id = ?"
        cats = np.array(cats)
        tp = []
        tn = []
        fp = []
        fn = []
        for idx in self.labeled_idx:
            cursor.execute(sql, (idx,))
            result = cursor.fetchall()[0]
            label, logits = result
            label = np.array(json.loads(label)).reshape(-1)
            pred = sigmoid(np.array(json.loads(logits))) > 0.5 #TODO: not support rules now
            g = np.any(label[cats].any() > 0)
            p = np.any(pred[cats].any() > 0)
            # import IPython; IPython.embed(); exit()
            if g == True and p == True:
                tp.append(idx)
            elif g == True and p == False:
                fn.append(idx)
            elif g is False and p == True:
                fp.append(idx)
            elif g == False and p == False:
                tn.append(idx)
        if match_type == "tp":
            return tp
        elif match_type == "tn":
            return tn
        elif match_type == "fp":
            return fp
        elif match_type == "fn":
            return fn
        elif match_type == "p":
            return tp + fp
        elif match_type == "n":
            return tn + fn
        else:
            raise ValueError("unsupported match type")

    def get_important_labels(self, idxs, _cats):
        res = {}
        for idx in idxs:
            activation = self.database_fetch_by_idx(idx, ["activations"])
            activation = json.loads(activation)
            for act in activation:
                text = act["text"]
                cats = act["cats"]
                for _, c in enumerate(cats):
                    if c in _cats:
                        if text not in res:
                            res[text] = []
                        res[text].append(idx)
        for text in res:
            res[text] = list(set(res[text]))
        return res


    def get_mismatch(self):
        if self.mismatch is not None:
            return self.mismatch.copy()
        mismatch_path = os.path.join(self.data_root, "mismatch.pkl")
        if os.path.exists(mismatch_path):
            logger.info("using mismatch buffer.")
            self.mismatch = pickle_load_data(mismatch_path)
        else:
            image_labels = self.get_category_pred(label_type="all", data_type="image")
            text_labels = self.get_category_pred(label_type="all", data_type="text")
            self.mismatch = (image_labels!=text_labels)
            pickle_save_data(mismatch_path, self.mismatch)
        return self.mismatch.copy()

    def get_mean_confidence(self):
        if self.mean_confidence is not None:
            return self.mean_confidence.copy()
        confidence_path = os.path.join(self.data_root, "confidence.pkl")
        if os.path.exists(confidence_path):
            logger.info("using confidence buffer.")
            self.mean_confidence = pickle_load_data(confidence_path)
        else:
            self.mean_confidence = []
            for i in range(len(self.train_idx)):
                conf = np.array(self.get_detection_result(i))[:, -2].mean()
                self.mean_confidence.append(conf)
            self.mean_confidence = np.array(self.mean_confidence)
            pickle_save_data(confidence_path, self.mean_confidence)
        return self.mean_confidence.copy()

    def get_category_pred(self, label_type="unlabeled", data_type="text", threshold=None):
        if threshold is None:
            threshold = self.conf_thresh
        if not isinstance(label_type, str) and isinstance(label_type, list):
            idxs = label_type
            label_type_text = "idx"
        elif label_type == "all":
            idxs = self.train_idx
            label_type_text = label_type
        elif label_type == "labeled":
            idxs = self.labeled_idx
            label_type_text = label_type
        elif label_type == "unlabeled":
            idxs = self.unlabeled_idx
            label_type_text = label_type
        else:
            raise ValueError("unsupported label type")
        logger.debug("begin get category pred with {} in {}".format(label_type_text, data_type))
        preds = []
        buffer_file = os.path.join(self.data_root, \
            "pred_buffer_{}_{}_thresh_{}.npy".format(label_type_text, data_type, threshold))
        if os.path.exists(buffer_file) and label_type_text != "idx":
            logger.info("using pred buffer: {}".format(buffer_file))
            preds = np.load(buffer_file)
            return preds
        if data_type == "text":
            for idx in tqdm(idxs):
                logit, image_output = self.database_fetch_by_idx(idx, ["logits", "image_output"])
                pred = sigmoid(np.array(json.loads(logit))) > 0.5
                image_output = np.array(json.loads(image_output)) > 0.5
                preds.append((image_output + pred).astype(float))
            preds = np.array(preds)
        elif data_type == "image":
            for idx in tqdm(idxs):
                detection = self.database_fetch_by_idx(idx, ["detection"])
                detection = np.array(json.loads(detection)) #[:,-1].astype(int)
                conf_detection = detection[detection[:, -2] > threshold].astype(np.float32)
                cats = conf_detection[:, -1].astype(int)
                cats = np.array(list(set(cats))).astype(int)
                pred = np.zeros(len(self.class_name))
                pred[cats] = 1
                preds.append(pred)
            preds = np.array(preds)
        else:
            raise ValueError("unsupported data type")
        
        if label_type_text != "idx":
            np.save(buffer_file, preds)
        logger.debug("finish get category pred with {} in {}".format(label_type_text, data_type))
        return preds
    
    def get_groundtruth_labels(self, label_type="unlabeled"):
        logger.debug("begin get groundtruth category with {}".format(label_type))
        if not isinstance(label_type, str) and isinstance(label_type, list):
            idxs = label_type
            label_type_text = "idx"
        elif label_type == "all":
            idxs = self.train_idx
        elif label_type == "labeled":
            idxs = self.labeled_idx
        elif label_type == "unlabeled":
            idxs = self.unlabeled_idx
        else:
            raise ValueError("unsupported label type")
        gt = []
        for idx in idxs:
            label = self.database_fetch_by_idx(idx, ["labels"])
            label = np.array(json.loads(label))
            gt.append(label)
        gt = np.array(gt)
        logger.debug("finish get groundtruth category pred with {}".format(label_type))
        return gt.astype(int)

    def get_image(self, idx):
        image_id = self.ids[idx]
        phase = "train2017_square"
        if idx in self.val_idx:
            phase = "val2017"
        img_path = os.path.join(self.data_all_step_root, \
            phase, "%012d.jpg" %(image_id))
        if not os.path.exists(img_path):
            img_path = os.path.join(config.raw_data_root, \
                "coco17_raw_data", phase, "%012d.jpg" %(image_id))
        return img_path 
    
    def get_origin_image(self, idx):
        image_id = self.ids[idx]
        phase = "train2017"
        if idx in self.val_idx:
            phase = "val2017"
        img_path = os.path.join(self.data_all_step_root, \
            phase, "%012d.jpg" %(image_id))
        if not os.path.exists(img_path):
            img_path = os.path.join(config.raw_data_root, \
                "coco17_raw_data", phase, "%012d.jpg" %(image_id))
        print("iamge_path", img_path)
        return img_path 
    
    def get_text(self, query):
        cursor = self.conn.cursor()
        sql = "select (cap) from annos where id = ?"
        word = query["word"]
        idxs = self.current_wordcloud[word]
        idxs = list(set(idxs))
        texts = []
        for idx in idxs:
            # anno = self.annos[idx]
            # caps = anno["caption"]
            result = cursor.execute(sql, (idx,))
            result = cursor.fetchall()[0]
            caps = result[0]
            # caps = [c + " " for c in caps]
            # caps = "".join(caps)
            text = {
                "message": caps,
                "active": True,
                "id": idx
            }
            texts.append(text)
        return texts

    def get_single_text(self, idx):
        cursor = self.conn.cursor()
        sql = "select (cap) from annos where id = ?"
        result = cursor.execute(sql, (idx,))
        result = cursor.fetchall()[0]
        caps = result[0]
        return caps


    def get_word(self, cats, match_type):
        self.current_text_idxs = self.get_labeled_id_by_type(cats, match_type)
        # print("current_text_idxs", self.current_text_idxs)
        self.current_wordcloud = self.get_important_labels(self.current_text_idxs, cats)
        words = [[k, len(self.current_wordcloud[k])] for k in self.current_wordcloud]
        return words

    def get_tfidf(self, type="labeled"):
        idxs = self.labeled_idx
        texts = [self.annos[idx]["extracted_labels"]["string"] for idx in idxs]
        for i in range(len(texts)):
            t = [s + " " for s in texts[i]]
            t = "".join(t)
            texts[i] = t
        tfidf, vocals = TFIDFTransform(texts)
        return tfidf, vocals

    def visuzalizing_groundtruth(self, idx):
        img_path, gt, det = self.get_image(idx)
        for g in gt:
            g[-1] = self.class_name[g[-1]]
        for d in det:
            d[-1] = self.class_name[d[-1]]
        im = draw_box(img_path, gt)
        tmp_dir = os.path.join(self.data_root, "result")
        check_dir(tmp_dir)
        cv2.imwrite(os.path.join(tmp_dir, "{}_{}.jpg".format(idx, "gt")), im)
    
    def visualizing_prediction(self, idx):
        None
