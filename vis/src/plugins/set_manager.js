import {getTextWidth} from "../plugins/global"

// function unique(arr){
//     return Array.from(new Set(arr));
// }

function set_unique(arr){
    let res = [];
    let keys = [];
    for (let i = 0; i < arr.length; i++){
        if (keys.indexOf(arr[i].type) == -1){
            keys.push(arr[i].type);
            res.push(arr[i]);
        }
    }
    return res;
}

const SetManager = function (text_width){
    let that = this;
    that.text_width = text_width;

    that.selected_nodes = [];

    this.update_selected_nodes = function(selected_nodes){
        that.selected_nodes = selected_nodes;
        let right_max = selected_nodes.map(d => 
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

    this.update_tree_node_position = function(tree_node_position){
        that.tree_node_group_x = tree_node_position.x;
        that.tree_node_group_y = tree_node_position.y;
    }


    this.get_sets = function(){
        let arr = that.selected_nodes.map(d => d.data.sets);
        arr = Array.prototype.concat.call(...arr);
        that.arr = set_unique(arr);
        console.log("arr in get_sets", that.arr);
        that.filter_and_sort();
        that.set_to_display.forEach(function(d, i){
            d.x = that.set_left;
            d.y = i * that.set_height + that.set_margin / 2;
            d.y_center = d.y + (that.set_height - that.set_margin) / 2;
            d.width = that.set_width - that.set_margin;
            d.height = that.set_height - that.set_margin;
        });

        that.get_set_links();
        return [that.set_to_display, that.set_links]
    }

    this.get_set_links = function(){
        that.set_links = [];
        for (let i = 0; i < that.selected_nodes.length; i++){
            let node = that.selected_nodes[i];

            let source = {
                "x": node.x + that.text_width + that.tree_node_group_x,
                "y": node.y + that.tree_node_group_y
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

    this.filter_and_sort = function(){
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
    }
}

export {SetManager}