import numpy as np
import os 
import cv2

from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import pickle_load_data, pickle_save_data
from ..utils.helper_utils import json_load_data, json_save_data, sigmoid
from ..utils.helper_utils import draw_box,check_dir
from ..database_utils.utils import decoding_categories, encoding_categories
from ..database_utils.utils import TFIDFTransform, rule_based_processing, get_precision_and_recall

DEBUG = True

class Data(object):
    def __init__(self, dataname, suffix=""):
        self.dataname = dataname 
        self.data_root = os.path.join(config.data_root, self.dataname)
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
        filename = config.processed_dataname
        if DEBUG:
            filename = config.debug_processed_dataname
        processed_data_filename = os.path.join(self.data_root, \
            filename.format(self.suffix))
        processed_data = json_load_data(processed_data_filename)
        self.processed_data = processed_data
        self.class_name = processed_data[config.class_name]
        self.X = processed_data[config.X_name]
        self.annos = processed_data[config.annos_name]
        self.detections = processed_data[config.detection_name]
        self.ids = processed_data[config.ids_name]
        self.labeled_idx = processed_data["labeled_idx"]
        self.train_idx = processed_data[config.train_idx_name]
        self.unlabeled_idx = [i for i in self.train_idx if i not in self.labeled_idx]
        self.val_idx = processed_data[config.valid_idx_name]
        self.test_idx = processed_data[config.test_idx_name]
        self.redundant_idx = processed_data[config.redundant_idx_name]
        self.image_by_type = processed_data["image_by_type"]
        self.categories = processed_data["categories"]
        self.add_info = processed_data[config.add_info_name]

        # load hierarchy
        self.tree = json_load_data(os.path.join(self.data_root, "hierarchy-abbr.json"))

        logger.info("end loading data from processed data!")

    def get_precision_and_recall(self):
        labels = []
        for i in self.labeled_idx:
            el = self.annos[i]["extracted_labels"]
            el["rule_logit"] = rule_based_processing(el)
            labels.append(el)
        self.labeled_p, self.precision, self.recall = get_precision_and_recall(labels)

    def get_captions_by_word_and_cat(self, word, cat):
        ids = self.labeled_extracted_labels_by_cat[cat][word]
        ids = [i["id"] for i in ids]
        ids = list(set(ids))
        caps = [self.annos[i]["caption"] for i in ids]
        return caps

    def get_labels_importance(self):
        # labels statistic
        extracted_labels_by_cat = {}
        labeled_extracted_labels_by_cat = {}
        for i in range(len(self.class_name)):
            extracted_labels_by_cat[i] = {}
            labeled_extracted_labels_by_cat[i] = {}
        for idx in self.train_idx:
            if idx in self.labeled_idx:
                by_cat = labeled_extracted_labels_by_cat
            else:
                by_cat = extracted_labels_by_cat
            img_id = self.ids[idx]
            extracted_labels = self.annos[idx]["extracted_labels"]
            for act in extracted_labels["activations"]:
                string_idx = act["idx"]
                text = act["text"]
                cats = act["cats"]
                probs = act["probs"]
                for i, c in enumerate(cats):
                    if text not in by_cat[c]:
                        by_cat[c][text] = []
                    by_cat[c][text].append({
                        "id": idx,
                        "prob": probs[i]
                    })
        self.extracted_labels_by_cat = extracted_labels_by_cat
        self.labeled_extracted_labels_by_cat = labeled_extracted_labels_by_cat

    def get_hypergraph(self):
        tree = self.get_tree()
        
        leaf_node = []
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            if len(node["children"]) == 0:
                leaf_node.append(node)
            visit_node.extend(node["children"])

        # name to id map
        name_2_id = {}
        for idx, name in enumerate(self.class_name):
            name_2_id[name.strip("\n")] = idx
        
        id_to_leaf = {}
        for node in leaf_node:
            node["cat_id"] = name_2_id[node["name"]]
            node["sets"] = []
            id_to_leaf[name_2_id[node["name"]]] = node

        set_list = self.get_set()
        for s in set_list:
            categories = decoding_categories(s)
            for c in categories:
                id_to_leaf[c]["sets"].append(s)


        # def get_counts(ids):
        #     preds = []
        #     for id in ids:
        #         try:
        #             logit = self.annos[id]["extracted_labels"]["logits"]
        #         except:
        #             import IPython; IPython.embed(); exit()
        #         pred = sigmoid(np.array(logit)) > 0.5
        #         preds.append(pred.reshape(-1))
        #     preds = np.array(preds)
        #     p = preds.sum(axis=0) / preds.shape[0]
        #     return p
        # labeled_p = get_counts(self.labeled_idx)
        # unlabeled_p = get_counts(self.unlabeled_idx)
        # import IPython; IPython.embed(); exit()

        if DEBUG:
            for i in range(len(self.class_name)):
                leaf = id_to_leaf[i]
                leaf["precision"] = 1
                leaf["recall"] = 1
        else:
            self.get_precision_and_recall()
            for i in range(len(self.class_name)):
                leaf = id_to_leaf[i]
                leaf["precision"] = self.precision[i]
                leaf["recall"] = self.recall[i]

        return tree, set_list

    def get_tree(self):
        return self.tree

    def get_set(self):
        all_types = self.image_by_type.keys()
        types = []
        for t in all_types:
            if len(self.image_by_type[t]) > 50 and len(t) > 0:
                types.append(t)
        return types        

    def get_image(self, idx):
        gt = self.annos[idx]["bbox"]
        det = self.detections[idx]["bbox"]
        image_id = self.ids[idx]
        phase = "train2017"
        if idx in self.val_idx:
            phase = "val2017"
        img_path = os.path.join(self.data_root, phase, "%012d.jpg" %(image_id))
        return img_path, gt, det
    
    def get_text(self, idx):
        None
    
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
