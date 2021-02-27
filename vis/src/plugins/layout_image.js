// import * as d3 from "d3"
// import {TreeCut} from "./treecut"

const image_cluster_list_layout = function(parent){
    let that = this;
    that.parent = parent;


    this.get_set_layout_from_parent = function(){
        that.layout_height = that.parent.layout_height;
        that.set_height = that.parent.set_height;
        that.set_left = that.parent.set_left;
        that.set_width = that.parent.set_width;
        that.set_margin = that.parent.set_margin;
    };
    this.get_set_layout_from_parent();

    this.update_parent_set_layout = function(data){
        that.parent.set_num = data.length;
        that.parent.set_height = that.layout_height / that.parent.set_num - 2;
        that.parent.image_height = that.set_height * 0.9;
    };
    
    let mean = function(arr){
        let sum = 0;
        for(let i = 0; i < arr.length; i++){
            sum += arr[i];
        }
        return sum / arr.length;
    };

    this.reorder = function(data){
        data.forEach( d => {
            let nodes = d.connected_nodes;
            let ys = nodes.map(n => n.y);
            d.order = mean(ys);
        })
        data.sort((a,b) => a.order - b.order);
        return data;
    }

    this.layout = function(data){
        this.update_parent_set_layout(data);
        this.get_set_layout_from_parent();

        data = this.reorder(data);

        data.forEach((d, i) => {
            d.x = that.set_left;
            // d.x = (d.depth - 1) * that.x_delta;
            d.y = i * that.set_height + that.set_margin / 2;
            d.y_center = d.y + (that.set_height - that.set_margin) / 2;
            d.height = that.set_height - that.set_margin;
            d.width = that.set_width - that.set_margin;
        });
        return data;
    }
}

export {image_cluster_list_layout}