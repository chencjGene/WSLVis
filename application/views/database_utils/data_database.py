import numpy as np
import os 
import cv2
import sqlite3
import json

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data, sigmoid
from ..utils.helper_utils import draw_box,check_dir
from ..database_utils.utils import decoding_categories, encoding_categories
from ..database_utils.utils import TFIDFTransform, rule_based_processing, get_precision_and_recall

DEBUG = False

class TreeHelper(object):
    def __init__(self, tree, class_name):
        self.tree = tree
        self.class_name = class_name
        
        # process
        self.cat_id_2_node = {}
        self.tree_node_id_2_node = {}
        self.name_2_id = {}

        # name to id map
        for idx, name in enumerate(self.class_name):
            self.name_2_id[name.strip("\n")] = idx

        tree = self.get_tree()
        leaf_node = []
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            self.tree_node_id_2_node[node["id"]] = node
            visit_node = visit_node[:-1]
            if len(node["children"]) == 0:
                leaf_node.append(node)
            visit_node.extend(node["children"])
        
        for node in leaf_node:
            node["cat_id"] = self.name_2_id[node["name"]]
            node["sets"] = []
            self.cat_id_2_node[self.name_2_id[node["name"]]] = node

    def get_tree(self):
        return self.tree
    
    def get_node_by_cat_id(self, cat_id):
        return self.cat_id_2_node[cat_id]
    
    def get_node_by_tree_node_id(self, tree_node_id):
        return self.tree_node_id_2_node[tree_node_id]
    
    def get_cat_id_by_name(self, name):
        return self.name_2_id[name]

    def get_all_leaf_descendants(self, node):
        leaf_node = []
        visit_node = [node]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            if len(node["children"]) == 0:
                leaf_node.append(node)
            visit_node.extend(node["children"])
        return leaf_node


class Data(object):
    def __init__(self, dataname, suffix="step0"):
        self.dataname = dataname 
        self.data_all_step_root = os.path.join(config.data_root, self.dataname)
        self.data_root = os.path.join(config.data_root, self.dataname, suffix)
        self.suffix = suffix
    
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
        self.image_by_type = processed_data["image_by_type"]
        self.categories = processed_data["categories"]
        self.add_info = processed_data[config.add_info_name]

        database_file = os.path.join(self.data_root, "database.db")
        self.conn = sqlite3.connect(database_file, check_same_thread=False)
        # self.cursor = self.conn.cursor()

        # load hierarchy
        tree = json_load_data(os.path.join(self.data_all_step_root, "hierarchy-abbr.json"))
        self.tree_helper = TreeHelper(tree, self.class_name)

        logger.info("end loading data from processed data!")

    def database_fetch_by_idx(self, idx, keys):
        # id, cap, bbox, logits, labels, activations, string, detection
        cursor = self.conn.cursor()
        keys = "".join([k + ", " for k in keys]).strip(", ")
        sql = "select {} from annos where id = ?".format(keys)
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0]
        if len(res) == 1:
            return res[0]
        else:
            return res

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

    def get_captions_by_word_and_cat(self, word, cat):
        ids = self.labeled_extracted_labels_by_cat[cat][word]
        ids = [i["id"] for i in ids]
        ids = list(set(ids))
        caps = [self.annos[i]["caption"] for i in ids]
        return caps

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

    def get_hypergraph(self):
        set_list = self.get_set()
        for s in set_list:
            categories = decoding_categories(s)
            for c in categories:
                self.tree_helper.get_node_by_cat_id(c)["sets"].append(s)

        self.get_labeled_importance()

        if DEBUG:
            for i in range(len(self.class_name)):
                leaf = self.tree_helper.get_node_by_cat_id(i)
                leaf["precision"] = 1
                leaf["recall"] = 1
        else:
            self.get_precision_and_recall()
            for i in range(len(self.class_name)):
                leaf = self.tree_helper.get_node_by_cat_id(i)
                leaf["precision"] = self.precision[i]
                leaf["recall"] = self.recall[i]
                leaf["words"] = [[k, len(self.labeled_extracted_labels_by_cat[i][k])] 
                    for k in self.labeled_extracted_labels_by_cat[i].keys()]

        return self.tree_helper.get_tree(), set_list


    def get_set(self):
        all_types = self.image_by_type.keys()
        types = []
        for t in all_types:
            if len(self.image_by_type[t]) > 50 and len(t) > 0:
                types.append(t)
        return types        

    def get_category_pred(self, label_type="unlabeled", data_type="text"):
        logger.info("begin get category pred with {} in {}".format(label_type, data_type))
        if label_type == "all":
            idxs = self.train_idx
        elif label_type == "labeled":
            idxs = self.labeled_idx
        elif label_type == "unlabeled":
            idxs = self.unlabeled_idx
        else:
            raise ValueError("unsupported label type")
        preds = []
        if data_type == "text":
            for idx in idxs:
                logit = self.database_fetch_by_idx(idx, ["logits"])
                pred = sigmoid(np.array(json.loads(logit))) > 0.5
                preds.append(pred.astype(float))
            preds = np.array(preds)
        elif data_type == "image":
            for idx in idxs:
                detection = self.database_fetch_by_idx(idx, ["detection"])
                detection = np.array(json.loads(detection))[:,-1].astype(int)
                cats = np.array(list(set(detection))).astype(int) - 1
                pred = np.zeros(len(self.class_name))
                pred[cats] = 1
                preds.append(pred)
            preds = np.array(preds)
        else:
            raise ValueError("unsupported data type")
        logger.info("finish get category pred with {} in {}".format(label_type, data_type))
        return preds
    
    def get_groundtruth_labels(self, label_type="unlabeled"):
        logger.info("begin get groundtruth category with {}".format(label_type))
        if label_type == "all":
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
        logger.info("finish get groundtruth category pred with {}".format(label_type))
        return gt.astype(int)

    def get_image(self, idx):
        gt = self.annos[idx]["bbox"]
        det = self.detections[idx]["bbox"]
        image_id = self.ids[idx]
        phase = "train2017"
        if idx in self.val_idx:
            phase = "val2017"
        img_path = os.path.join(self.data_root, phase, "%012d.jpg" %(image_id))
        return img_path, gt, det
    
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

    def get_word(self, query):
        tree_node_id = query["tree_node_id"]
        match_type = query["match_type"]
        node = self.tree_helper.get_node_by_tree_node_id(tree_node_id)
        leaf_node = self.tree_helper.get_all_leaf_descendants(node)
        cats = [n["cat_id"] for n in leaf_node]
        print("cats", cats)
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
