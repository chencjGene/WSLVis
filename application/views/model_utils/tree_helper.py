import numpy as np
import os

from ..utils.helper_utils import json_load_data, json_save_data

class TreeHelper(object):
    def __init__(self, tree=None, class_name=None, data_root=None):
        self.tree = tree
        self.class_name = class_name
        self.data_root = data_root
        if self.tree:
            self._init()

    def update(self, tree, class_name):
        self.tree = tree
        self.class_name = class_name
        self._init()

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

    def get_all_leaf_descendants_ids(self, node):
        leaf_node = self.get_all_leaf_descendants(node)
        return [n["id"] for n in leaf_node]

    def del_descendants(self):
        leaf_node = []
        visit_node = [self.tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            visit_node.extend(node["children"])
            if "descendants_idx" in node:
                del node["descendants_idx"]

    def export_to_file(self, filename=None):
        if filename is None:
            filename = os.path.join(self.data_root, \
                "clustering_hierarchy.json")
        json_save_data(filename, self.tree)

    def import_from_file(self, filename=None):
        if filename is None:
            filename = os.path.join(self.data_root, \
                "clustering_hierarchy.json")
        self.tree = json_load_data(filename)
        self._init()

class TextTreeHelper(TreeHelper):
    def __init__(self, tree=None, class_name=None, data_root=None):
        super(TextTreeHelper, self).__init__(tree, class_name, data_root)

    def _init(self):
        # process
        self.cat_id_2_node = {}
        self.tree_node_id_2_node = {}
        self.name_2_id = {}

        # name to id map
        for idx, name in enumerate(self.class_name):
            self.name_2_id[name.strip("\n")] = idx
        id_count = idx + 1

        tree = self.get_tree()
        leaf_node = []
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            if len(node["children"]) == 0:
                leaf_node.append(node)
            if node["name"] in self.name_2_id:
                node["id"] = self.name_2_id[node["name"]]
            else:
                node["id"] = id_count
                id_count = id_count + 1
            self.tree_node_id_2_node[node["id"]] = node
            visit_node.extend(node["children"])
        
        for node in leaf_node:
            node["cat_id"] = self.name_2_id[node["name"]]
            node["sets"] = []
            self.cat_id_2_node[self.name_2_id[node["name"]]] = node

    def assign_precision_and_recall(self, precision, recall):
        for i in range(len(self.class_name)):
            leaf = self.get_node_by_cat_id(i)
            leaf["precision"] = precision[i]
            leaf["recall"] = recall[i]

    def assign_mismatch(self, mismatch):
        m = mismatch.sum(axis=0)
        for i in range(len(self.class_name)):
            leaf = self.get_node_by_cat_id(i)
            leaf["mismatch"] = int(m[i])

class ImageTreeHelper(TreeHelper):
    def __init__(self, tree=None, class_name=None):
        super(ImageTreeHelper, self).__init__(tree, class_name)
    
    def _init(self):
        # process
        self.cat_id_2_node = {}
        self.tree_node_id_2_node = {}
        self.name_2_id = {}

        # name to id map
        for idx, name in enumerate(self.class_name):
            self.name_2_id[name.strip("\n")] = idx
        id_count = idx + 1

        tree = self.get_tree()
        leaf_node = []
        visit_node = [tree]
        while len(visit_node) > 0:
            node = visit_node[-1]
            visit_node = visit_node[:-1]
            if len(node["children"]) == 0:
                leaf_node.append(node)
            if node["name"] in self.name_2_id:
                node["id"] = self.name_2_id[node["name"]]
            else:
                node["id"] = id_count
                id_count = id_count + 1
            self.tree_node_id_2_node[node["id"]] = node
            visit_node.extend(node["children"])
        
        for node in leaf_node:
            node["cat_id"] = self.name_2_id[node["name"]]
            node["sets"] = []
            self.cat_id_2_node[self.name_2_id[node["name"]]] = node