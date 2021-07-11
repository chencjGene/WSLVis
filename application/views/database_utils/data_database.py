import numpy as np
import os 
import cv2
import sqlite3
import json
from tqdm import tqdm
from time import time

from sklearn.metrics import precision_score, recall_score
from PIL import Image, ImageDraw, ImageFont

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data, sigmoid
from ..utils.helper_utils import draw_box,check_dir
from ..database_utils.utils import decoding_categories, encoding_categories
from ..database_utils.utils import TFIDFTransform, rule_based_processing, get_precision_and_recall
from .set_helper import SetHelper

DEBUG = False

class RoIMaxPooling2d(object):  # torch.nn.AdaptiveMaxPool2d
    def __init__(self, out_size):
        self.w, self.h = out_size  # (w, h)

    def __call__(self, x: np.ndarray):
        x = x.transpose(2, 0, 1)
        (channels, width, height) = x.shape  # (channels, width, height)
        out = np.zeros([channels, self.w, self.h])

        if x.shape[1] <= 1 or x.shape[2] <= 1:
            out[:, :min(x.shape[1], self.w), :min(x.shape[2], self.h)] = \
                x[:, :min(x.shape[1], self.w), :min(x.shape[2], self.h)]
            return out.reshape(-1)
        grid_w = (width + self.w - 1) // self.w
        grid_h = (height + self.h - 1) // self.h
        for ch in range(channels):  # channels
            for iw in range(self.w):  # width
                sw, ew = self.update_index(iw, grid_w)
                for ih in range(self.h):  # height
                    sh, eh = self.update_index(ih, grid_h)
                    out[ch, iw, ih] = np.max(x[ch][sw:ew, sh:eh])
        out = out.transpose(1, 2, 0)
        return out

    @staticmethod
    def update_index(idx, grid):
        start = idx * grid
        end = start + grid
        return  start, end

class DataBaseLoader(object):
    def __init__(self, dataname, step=0):
        self.dataname = dataname 
        self.suffix = "step" + str(step)
        self.step = step
        self.data_all_step_root = os.path.join(config.data_root, self.dataname)
        self.data_root = os.path.join(config.data_root, self.dataname, self.suffix)
        self.conf_thresh = 0.5

        self.image_features = None
        self.text_features = None
        self.detection_features = None

        self.detection_res_for_vis = None
        try:
            self.detection_res_for_vis = json_load_data(os.path.join(self.data_root,
                config.detection_res_for_vis_filename))
        except:
            logger.info("{} does not exist".format(config.detection_res_for_vis_filename))
            self.detection_res_for_vis = {}

        database_file = os.path.join(self.data_root, "database.db")
        print(database_file)
        self.conn = sqlite3.connect(database_file, check_same_thread=False)

        self.width_height = json_load_data(os.path.join(self.data_all_step_root, \
            "width_height.json"))

    def save_detection_res_for_vis_buffer(self):
        return json_save_data(os.path.join(self.data_root, config.detection_res_for_vis_filename),
            self.detection_res_for_vis)
        

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
        idx = int(idx)
        cursor = self.conn.cursor()
        sql = "select detection from annos where id = ?"
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0][0]
        res = json.loads(res)
        return res

    def get_anno_bbox_result(self, idx):
        idx = int(idx)
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
        sizes = [256, 256, 256, 512, 1024, 512]
        split_points = [0]
        sum = 0
        feature_id = 3
        for i in sizes:
            sum = sum + i
            split_points.append(sum)
        logger.info("split_points: {}".format(str(split_points)))
        self.image_features = \
            features[:, split_points[feature_id]: split_points[feature_id+1]]
        return self.image_features

    def get_detection_feature(self, img_id, bbox):
        if self.detection_features is None:
            # return self.detection_features
            detection_feature_path = os.path.join(self.data_root, "feature_map.npy")
            self.detection_features = np.load(detection_feature_path)
        feature = self.detection_features[img_id]
        img_path = self.get_origin_image(img_id)
        img = Image.open(img_path)
        width, height = img.size
        bbox = np.array(bbox) / np.array([width, height, width, height])
        feature_map_size = feature.shape[0]
        bbox = (bbox * feature_map_size + 0.49).astype(int)
        bbox[bbox < 0] = 0
        feature = feature[bbox[1]:bbox[3]+1, bbox[0]:bbox[2]+1]
        if np.array(feature.shape).all() == 0:
            return np.zeros(16)
        # out = feature.transpose(2, 0, 1).reshape(16, -1).mean(axis=1)
        output = RoIMaxPooling2d((2, 2))(feature).reshape(-1)
        # if np.isnan(out.max()):
        #     a = 1
        return output



    def get_detection_result_for_vis(self, idx, conf_thresh=None, cats_ids=None):
        if conf_thresh is None:
            conf_thresh = self.conf_thresh
        res = self.detection_res_for_vis.get(str(idx), None)
        if res is not None:
            return res
        w, h = self.width_height[idx]
        detection = self.get_detection_result(idx)
        detection = np.array(detection)
        conf_detection = detection[detection[:, -2] > conf_thresh].astype(np.float32)
        conf_detection[:, 4:6] = conf_detection[:, -2:]
        conf_detection = conf_detection[:, :6]
        if idx == 100724:
            conf_detection[:, 5] = 10
        # if cats_ids is not None:
        #     conf_detection = conf_detection.tolist()
        #     conf_detection = [d for d in conf_detection if d[-1] in cats_ids]
        #     conf_detection = np.array(conf_detection)
        gt_d = self.get_anno_bbox_result(idx)
        if len(conf_detection) > 0:
            conf_detection[:, 0] /= w
            conf_detection[:, 2] /= w # width
            conf_detection[:, 1] /= h
            conf_detection[:, 3] /= h # height
            # conf_detection[:, 2] += conf_detection[:, 0] # max x
            # conf_detection[:, 3] += conf_detection[:, 1] # max y
            conf_detection[:, :4] = np.clip(conf_detection[:, :4], 0, 1)
            # conf_detection[:, 2] -= conf_detection[:, 0] # width
            # conf_detection[:, 3] -= conf_detection[:, 1] # height
            conf_detection = np.round(conf_detection, 3)
            conf_detection = conf_detection.tolist()
        else:
            conf_detection = []
        res = {"idx": idx, "w": w, "h": h, "d": conf_detection, "gt_d": gt_d}
        self.detection_res_for_vis[str(idx)] = res
        return res


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
        logger.info("get precision and recall")
        label_type = "labeled"
        preds = self.get_category_pred(label_type=label_type, data_type="text-only")
        gt = self.get_groundtruth_labels(label_type=label_type)
        print("preds.shape", preds.shape)
        self.precision = []
        self.recall = []
        self.correctness = (preds == gt)
        for i in range(len(self.class_name)):
            pre = precision_score(gt[:, i], preds[:, i])
            if pre == 0:
                pre = 0.01
            rec = recall_score(gt[:, i], preds[:, i])
            if rec == 0:
                rec = 0.01
            self.precision.append(pre)
            self.recall.append(rec)
        

    def get_labeled_id_by_type(self, cats: list, match_type: str) -> list:
        cats = np.array(cats)
        tp = []
        tn = []
        fp = []
        fn = []
        label_type = "labeled"
        # if self.step <= 2:
        #     preds = self.get_category_pred(label_type=label_type, data_type="text-only")
        # else:
        preds = self.get_category_pred(label_type=label_type, data_type="text")
        gt = self.get_groundtruth_labels(label_type=label_type)
        for idx in self.labeled_idx:
            label = gt[idx]
            pred = preds[idx]
            g = np.any(label[cats].any() > 0)
            p = np.any(pred[cats].any() > 0)
            if g == True and p == True:
                tp.append(idx)
            elif g == True and p == False:
                fn.append(idx)
            elif g == False and p == True:
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
            text_labels = self.get_category_pred(label_type="all", data_type="text-only")
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
        elif label_type == "val":
            idxs = self.val_idx
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
        elif data_type == "text-only":
            for idx in tqdm(idxs):
                logit = self.database_fetch_by_idx(idx, ["logits"])
                pred = sigmoid(np.array(json.loads(logit))) > 0.5
                preds.append((pred).astype(float))
            preds = np.array(preds)
        elif data_type == "image-for-cls":
            for idx in tqdm(idxs):
                image_output = self.database_fetch_by_idx(idx, ["image_output"])
                image_output = np.array(json.loads(image_output)) > 0.5
                preds.append((image_output).astype(float))
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
        elif label_type == "val":
            idxs = self.val_idx
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
        # print("iamge_path", img_path)
        return img_path 
    
    def get_text_by_word(self, query):
        cursor = self.conn.cursor()
        sql = "select (cap) from annos where id = ?"
        word = query["word"]
        cat_ids = np.array(query["cat_id"])
        rules = query["rules"]
        print("rules", rules)
        # TODO
        keyword = []
        if len(rules) > 0:
            keyword = "restaurant"
        idxs = self.current_wordcloud[word]
        idxs = list(set(idxs))
        labels = self.get_category_pred(label_type=idxs, data_type="text-only")
        correctness = self.correctness[np.array(idxs)][:, cat_ids]
        correctness = correctness.sum(axis=1)
        texts = []
        # import IPython; IPython.embed(); 
        for i, idx in enumerate(idxs):
            # anno = self.annos[idx]
            # caps = anno["caption"]
            result = cursor.execute(sql, (idx,))
            result = cursor.fetchall()[0]
            caps = result[0]
            label = labels[i]
            words = self.current_text_2_word[idx]
            if len(words) == 1 and words[0] == keyword:
                label[33] = 0
            # caps = [c + " " for c in caps]
            # caps = "".join(caps)
            text = {
                "message": caps,
                "active": True,
                "id": idx,
                "c": np.array(self.class_name)[label.astype(bool)].tolist()
                # "c": self.current_text_2_word[idx]
            }
            texts.append(text)
        return texts
    
    def get_text(self, query):
        cursor = self.conn.cursor()
        sql = "select (cap) from annos where id = ?"
        ids = np.array(query["ids"]).tolist()
        labels = self.get_category_pred(label_type=ids, data_type="text-only")
        texts = []
        for i, idx in enumerate(ids):
            # anno = self.annos[idx]
            # caps = anno["caption"]
            result = cursor.execute(sql, (int(idx),))
            result = cursor.fetchall()[0]
            caps = result[0]
            label = labels[i]
            # caps = [c + " " for c in caps]
            # caps = "".join(caps)
            text = {
                "message": caps,
                "active": True,
                "id": int(idx),
                "c": np.array(self.class_name)[label.astype(bool)].tolist()
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
        self.current_text_2_word = {}
        for key in self.current_wordcloud:
            idxs = self.current_wordcloud[key]
            for idx in idxs:
                if idx not in self.current_text_2_word:
                    self.current_text_2_word[idx] = []
                self.current_text_2_word[idx].append(key)
        # import IPython; IPython.embed(); exit()
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
