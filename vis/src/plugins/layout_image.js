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
        that.mini_set_height = that.parent.mini_set_height;
        that.large_set_height = that.parent.large_set_height; 
    };
    this.get_set_layout_from_parent();

    this.get_expand_set_id = function(){
        return that.parent.expand_set_id;
    }

    this.update_parent_set_layout = function(data){
        console.log("update_parent_set_layout");
        that.parent.set_num = data.length;
        that.parent.set_height = that.layout_height / that.parent.set_num - 2;
        that.parent.image_height = that.parent.set_height * 0.9;
        that.parent.mini_set_height = 20;
        that.parent.large_set_height = that.layout_height - 
            (that.parent.set_num - 1) * that.parent.mini_set_height;
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
        console.log("image layout");
        this.update_parent_set_layout(data);
        this.get_set_layout_from_parent();

        // data = this.reorder(data);
        let offset = 0;
        data.forEach((d) => {
            d.x = that.set_left;
            // d.x = (d.depth - 1) * that.x_delta;
            // d.y = i * that.set_height + that.set_margin / 2;
            // d.y_center = d.y + (that.set_height - that.set_margin) / 2;
            let w = d.id === that.get_expand_set_id() ? 
                that.large_set_height: that.mini_set_height;
            if (that.get_expand_set_id() === -1) w = that.set_height;
            d.y = offset;
            offset = offset + w + that.set_margin / 2;
            d.y_center = d.y + (w - that.set_margin) / 2;
            d.height = w - that.set_margin;
            d.width = that.set_width - that.set_margin;
        });
        return data;
    }
}

export {image_cluster_list_layout}