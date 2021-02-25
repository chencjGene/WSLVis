// import * as d3 from "d3"
// import {TreeCut} from "./treecut"

const image_tree_layout = function(nodeSize, layout_height){
    let that = this;
    that.x_delta = nodeSize[0];
    that.y_delta = nodeSize[1];
    that.layout_height = layout_height;

    this.layout = function(data){
        console.log("image_tree layout", data);
        data.children = data.all_children;
        data.eachBefore((d, i) => {
            d.x = (d.depth - 1) * that.x_delta;
            d.y = (i - 1) * that.y_delta;
        });
        return data.descendants();
    }
}

export {image_tree_layout}