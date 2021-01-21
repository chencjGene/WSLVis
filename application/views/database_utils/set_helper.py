import numpy as np
import json
import os
from tqdm import tqdm
from random import choice

from ..database_utils.utils import decoding_categories, encoding_categories
from ..utils.config_utils import config
from ..utils.log_utils import logger
from ..utils.helper_utils import json_load_data, json_save_data 

class SetHelper(object):
    def __init__(self, train_idx, width_height, conn, data_root, class_name):
        self.train_idx = train_idx
        self.width_height = width_height
        self.conn = conn
        self.data_root = data_root
        self.class_name = class_name
        self.conf_thresh = 0.5
        self.sets = {}
        self.sampled_sets = {}
        
        
        self._get_image_by_type()
        self._graph_construction()



    def _get_image_by_type(self):
        filename = os.path.join(self.data_root, "image_by_type.json")
        if os.path.exists(filename):
            logger.info("using image_by_type.json buffer")
            self.image_by_type = json_load_data(filename)
            return 

        self.image_by_type = {}
        for idx in tqdm(self.train_idx):
            det = self.get_detection_result(idx)
            category = [d[-1] for d in det if d[-2] > self.conf_thresh]
            cat_str = encoding_categories(category)
            if cat_str not in self.image_by_type:
                self.image_by_type[cat_str] = []
            self.image_by_type[cat_str].append(int(idx))
        json_save_data(filename, self.image_by_type)

    def _graph_construction(self):
        logger.info("begin graph construction in set helper")
        all_types = self.get_all_set_name()
        types = {}
        # calculate out links
        for t in all_types:
            cats = decoding_categories(t)
            links = []
            for s in all_types:
                cats_of_s = decoding_categories(s)
                if set(cats_of_s) > set(cats):
                    links.append(s)
            image_list = self.get_image_list_by_type(t, scope="all")
            types[t] = {
                "type": t,
                "num": len(image_list),
                "selected_image": self.get_image_list_by_type(t, \
                    scope="selected", with_wh=True),
                "out_links": links,
                "in_links": []
            }
        # calculate in links
        for t in types:
            out_links = types[t]["out_links"]
            for s in out_links:
                types[s]["in_links"].append(t)
        
        
        self.sets = types
        selected_sets = [name for name in self.sets.keys() \
            if len(self.sets[name]["out_links"]) == 0]
        
        # hierarchy clustering
        while len(selected_sets) > 1:
            set1 = choice(selected_sets) # TODO
            selected_sets.remove(set1)
            set2 = choice(selected_sets) # TODO
            selected_sets.remove(set2)
            cats = decoding_categories(set1) + decoding_categories(set2)
            set_name = encoding_categories(cats)
            self.sets[set_name] = {
                "type": set_name,
                "num": 0,
                "selected_image": [], # TODO,
                "out_links": [],
                "in_links": list(set(self.sets[set1]["in_links"] + \
                    self.sets[set2]["in_links"])) + [set1, set2]
            }
            # self.sets[set1]["out_links"].append(set_name)
            # self.sets[set2]["out_links"].append(set_name)
            for s in self.sets[set_name]["in_links"]:
                self.sets[s]["out_links"].append(set_name)
            selected_sets.append(set_name)

        logger.info("finish graph construction in set helper")

    def _graph_sampling(self):
        for t in self.sets:
            self.sets[t]["tmp_out_links"] = self.sets[t]["out_links"].copy()
            self.sets[t]["visited"] = False
        selected_sets = [name for name in self.sets.keys() \
            if len(self.sets[name]["out_links"]) == 0]
        self.selected_sets = []
        while len(self.selected_sets) + len(selected_sets) < 10:
            selected_one_with_largest_gain = choice(selected_sets) # TODO
            self.sets[selected_one_with_largest_gain]["visited"] = True
            if self.sets[selected_one_with_largest_gain]["num"] > 0:
                self.selected_sets.append(selected_one_with_largest_gain)
            for s in self.sets[selected_one_with_largest_gain]["in_links"]:
                self.sets[s]["tmp_out_links"].remove(selected_one_with_largest_gain)
            selected_sets = [name for name in self.sets.keys() \
            if len(self.sets[name]["tmp_out_links"]) == 0 and self.sets[name]["visited"] is False]
            print("while", len(self.selected_sets), len(selected_sets))
        self._selected_sets = self.selected_sets + selected_sets
        self.selected_sets = {}
        for s in self._selected_sets:
            self.selected_sets[s] = self.sets[s]
        print(self.selected_sets.keys())
        return self.selected_sets

    def get_set(self):
        self.sampled_sets = self._graph_sampling()
        return self.sampled_sets


    def get_all_set_name(self):
        all_types = self.image_by_type.keys()
        types = []
        for t in all_types:
            if len(self.image_by_type[t]) > 50 and len(t) > 0:
                types.append(t)
        return types

    def get_detection_result(self, idx):
        cursor = self.conn.cursor()
        sql = "select detection from annos where id = ?"
        cursor.execute(sql, (idx,))
        res = cursor.fetchall()[0][0]
        res = json.loads(res)
        return res

    def get_image_list_by_type(self, t, scope="selected", with_wh = False):
        def add_width_height(idx):
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
        if scope == "all":
            if with_wh:
                return [add_width_height(i) for i in self.image_by_type[t]]
            else:
                return self.image_by_type[t]
        elif scope == "selected":
            if with_wh:
                return [add_width_height(i) for i in self.image_by_type[t][-10:]]
            else:
                return self.image_by_type[t][-10:]
