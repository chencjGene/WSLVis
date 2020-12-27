import {getTextWidth} from "../plugins/global"

function unique(arr){
    return Array.from(new Set(arr));
}

const SetManager = function (){
    let that = this;

    that.leaf_nodes = [];

    this.update_leaf_nodes = function(leaf_nodes){
        that.leaf_nodes = leaf_nodes;
        let right_max = leaf_nodes.map(d => 
            d.y + getTextWidth(d.data.name, "16px Roboto, sans-serif"));
        that.right_max = Math.max(...right_max);
    }

    this.update_layout = function(mat){
        that.layout_width = mat.layout_width;
        that.layout_height = mat.layout_height;
        that.set_left = mat.set_left;
        that.set_width = mat.set_width;
        that.set_margin = mat.set_margin;
        that.set_height = mat.set_height;
    }

    // this.update_tree_root = function(x, y){
    //     that.tree_x = x;
    //     that.tree_y = y;
    //     console.log("update tree root", that.tree_x, that.tree_y);
    // }

    this.get_sets = function(){
        let arr = that.leaf_nodes.map(d => d.data.sets);
        arr = Array.prototype.concat.call(...arr);
        that.arr = unique(arr);
        console.log("arr in get_sets", arr);
        // TODO: filtering or sorting
        let num_to_display = 
            Math.floor(that.layout_height / that.set_height);
        that.set_to_display = [];
        that.set_map = [];
        for (let i = 0; i < num_to_display; i++){
            that.set_to_display.push({
                "name": that.arr[i]
            });
            that.set_map[that.arr[i]] = that.set_to_display[i];
        }
        that.set_to_display.forEach(function(d, i){
            d.x = that.set_left;
            d.y = i * that.set_height + that.set_margin / 2;
            d.y_center = d.y + (that.set_height - that.set_margin) / 2;
            d.width = that.set_width - that.set_margin;
            d.height = that.set_height - that.set_margin;
        });

        that.get_set_links();
        return {
            "sets": that.set_to_display,
            "set_links": that.set_links
        };
    }

    this.get_set_links = function(){
        that.set_links = [];
        for (let i = 0; i < that.leaf_nodes.length; i++){
            let node = that.leaf_nodes[i];
            let text_width = getTextWidth(node.data.name, "16px Roboto, sans-serif");

            let source = {
                "x": node.x + text_width + 15,
                "y": node.y 
            };

            let turn_point = {
                "x": that.right_max,
                "y": node.y
            }

            // console.log("node:", node);
            for (let j = 0; j < node.data.sets.length; j++){
                let set_name = node.data.sets[j];
                let set_node = that.set_map[set_name];
                if (!set_node) continue;
                let target = {
                    "x": set_node.x,
                    "y": set_node.y_center
                }
                that.set_links.push({
                    source, target, turn_point
                });
            }
        }
    }
}

export {SetManager}