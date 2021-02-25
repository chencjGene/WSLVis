// import * as d3 from "d3"
// import {TreeCut} from "./treecut"

const image_tree_layout = function(parent){
    let that = this;
    that.parent = parent;
    that.set_height = parent.set_height;
    that.set_left = parent.set_left;
    that.set_width = parent.set_width;
    that.set_margin = parent.set_margin;

    this.layout = function(data){
        console.log("image_tree layout", data);
        data.children = data.all_children;
        data.eachBefore((d, i) => {
            d.x = that.set_left;
            // d.x = (d.depth - 1) * that.x_delta;
            d.y = (i - 1) * that.set_height + that.set_margin / 2;
            d.height = that.set_height - that.set_margin;
            d.width = that.set_width - that.set_margin;
        });
        return data.descendants().filter(d => d.name != "root");
    }
}

export {image_tree_layout}