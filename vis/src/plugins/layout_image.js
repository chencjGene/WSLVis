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

    this.get_grid_data = function(){
        return that.parent.grid_data;
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
        let grids = [];
        let pos = {};
        if (that.get_expand_set_id()!==-1) [grids, pos] = that.grid_layout(data);
        return [data, grids, pos];
    }

    this.grid_layout = function(data){
        let grid_height = that.large_set_height;
        let grid_width = that.set_width;
        let side_length = 0;
        let offset_x = 0;
        let offset_y = 0;
        if (grid_height > grid_width){
            offset_y = (grid_height - grid_width) / 2;
            offset_x = that.set_left + 0;
            side_length = grid_width;
        }
        else{
            offset_y = 0;
            offset_x = that.set_left + (grid_width - grid_height) / 2;
            side_length = grid_height;
        }
        offset_y = offset_y + data.filter(d => d.id === that.get_expand_set_id())[0].y;
        console.log("offset_x, offset_y", offset_x, offset_y);

        let grid_data = that.get_grid_data();
        let grid_size = Math.ceil(Math.sqrt(grid_data.length));
        let cell_width = 1.0 / grid_size;
        grid_data.forEach(d => {
            d.x = offset_x + side_length * d.pos[0];
            d.y = offset_y + side_length * d.pos[1];
            d.width = cell_width * side_length;
        })
        return [grid_data, {offset_x, offset_y, side_length}];
    }
}

export {image_cluster_list_layout}