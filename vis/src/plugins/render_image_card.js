import * as Global from "../plugins/global";
import * as d3 from "d3";  

const ImageCards = function(parent){
    let that =this;
    that.parent = parent;
    that.server_url = that.parent.server_url;
    
    that.set_group = that.parent.set_group;
    that.grid_group = that.parent.grid_group;

    // animation
    that.create_ani = that.parent.create_ani;
    that.update_ani = that.parent.update_ani;
    that.remove_ani = that.parent.remove_ani;

    // 
    that.boundingbox_width = 3;
    
    // let labels = Array(); // Label layout
    // let img_width = 40;

    let margin_size = 20;
    let margin_top_size = 100;
    let plot_width = 800;
    let plot_height = 800;
    var offset_x = 0; // position of the left grid when the mode is "juxtaposition"
    var offset_y = 100;

    let mouse_pressed = false;
    let mouse_pos = {
        x: -1,
        y: -1
    };

    let relative_sampling_area = {
        x: 0,
        y: 0,
        w: 1,
        h: 1
    };
    let plot_x, plot_y = 1;

    this.get_set_layout_from_parent = function(){
        // set
        that.layout_height = that.parent.layout_height;
        that.set_height = that.parent.set_height;
        that.set_left = that.parent.set_left;
        that.set_width = that.parent.set_width;
        that.set_margin = that.parent.set_margin;
        that.image_height = that.parent.image_height;
        that.image_margin = that.parent.image_margin;
        that.text_height = that.parent.text_height;
    };
    this.get_set_layout_from_parent();

    this.set_focus_image = function(image){
        that.parent.set_focus_image(image);
    },

    this.set_expand_set_id = function(id){
        that.parent.set_expand_set_id(id);
    }

    this.get_expand_set_id = function(){
        return that.parent.expand_set_id;
    }

    this.sub_component_update = function(sets, vis_image_per_cluster, grids, grids_pos) {
        // update layout config
        that.get_set_layout_from_parent();

        // update state 
        that.vis_image_per_cluster = vis_image_per_cluster;
        that.grids = grids;
        offset_x = grids_pos.offset_x;
        offset_y = grids_pos.offset_y;
        plot_width = grids_pos.side_length;
        plot_height = grids_pos.side_length;
        Object.values(that.vis_image_per_cluster).forEach(d => {
            let x = that.image_margin;
            d.forEach(n => {
                n.vis_h = that.image_height;
                n.vis_w = that.image_height;
                n.x = x;
                x = x + n.vis_w + that.image_margin;
            })
        })
        console.log("image card sub component update", sets, grids);
        

        // update view
        that.e_sets = that.set_group.selectAll(".set").data(sets, d => d.id); 
        that.e_grids = that.grid_group.selectAll(".grid").data(grids, d => d.img_id);
        

        that.remove();
        that.update();
        that.create();
    };

    this.create = function(){
        that.set_create();
        that.grid_create();
    }

    this.set_create = function() {
        // set
        let set_groups = that.e_sets
            .enter()
            .append("g")
            .attr("class", "set")
            .attr("id", d => "set-" + d.id)
            .attr(
                "transform",
                (d) => "translate(" + d.x + ", " + d.y + ")"
            );
        set_groups
            .style("opacity", 0)
            .transition()
            .duration(that.create_ani)
            .delay(that.update_ani + that.remove_ani)
            .style("opacity", 1);

        // expand icon
        set_groups.append("rect")
            .attr("class", "expand-rect")
            .attr("x", -11)
            .attr("y", 0)
            .attr("width", 10)
            .attr("height", 10)
            .style("rx", 3)
            .style("ry", 3)
            .style("fill", "white")
            .style("stroke", "gray")
            .style("stroke-width", 1)
            .on("click", (_, d) => {
                if (d.id === that.get_expand_set_id()){
                    that.set_expand_set_id(-1);
                }
                else{
                    that.set_expand_set_id(d.id);
                }
            })
        
        set_groups.append("path")
            .attr("class", "expand-path")
            .style("stroke", "none")
            .style("fill", "gray")
            .attr("d", Global.plus_path_d(-11, 0, 10, 10, 2));

        set_groups
            .append("rect")
            .attr("class", "background")
            .style("fill", "white")
            .style("stroke", "#e0e0e0")
            .style("stroke-width", 1)
            .attr("width", d => d.width)
            .attr("height", d => d.height);
        
        that.image_groups = set_groups.selectAll("g.detection-result")
            .data(d => that.vis_image_per_cluster[d.id]);
        let g_image_groups = that.image_groups.enter()
            .append("g")
            .attr("class", "detection-result")
            .attr(
                "transform",
                (d) => "translate(" + d.x + ", " + that.image_margin / 2 + ")"
            );
        
            g_image_groups.append("image")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", d => d.vis_w)
            .attr("height", d => d.vis_h)
            .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
            .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none")
            .attr("href", d => that.server_url + `/image/image?filename=${d.idx}.jpg`)
            .on("click", (_, d) => {
                console.log("click image", d);
                that.set_focus_image(d);
            })
        
        that.box_groups = g_image_groups.selectAll("rect.box")
            .data(d => {
                let dets = d.d;
                let res = [];
                for (let i = 0; i < dets.length; i++){
                    let x = d.vis_w * dets[i][0];
                    let width = d.vis_w * (dets[i][2] - dets[i][0]);
                    let y = d.vis_h * dets[i][1];
                    let height = d.vis_h * (dets[i][3] - dets[i][1]);
                    res.push({x, y, width, height});
                }
                return res;
            });
        that.box_groups.enter()
            .append("rect")
            .attr("class", "box")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("width", d => d.width)
            .attr("height", d => d.height)
            .style("fill", "none")
            .style("stroke", "green")
            .style("stroke-width", 1)
            .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
            .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");

            
    };

    this.grid_create = function(){
        let grid_groups = that.e_grids.enter()
            .append("g")
            .attr("class", "grid")
            .attr("transform", d => "translate(" + (d.x) + ", " +  (d.y) + ")")
            // .on('click', function(d) {

            // })
            .on("mouseover", function() {
                d3.select(this).select("rect")
                    .style("stroke-width",  2.0);
            })
            .on("mouseout", function() {
                d3.select(this).select("rect")
                    .style("stroke-width", 0.0);
            })
            // TOOD: mouseover, mouseout

        grid_groups.append("rect")
            .attr("class", "boundingbox")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", d => d.width)
            .attr("height", d => d.width)
            .style("fill", d => d.mismatch > 0 ? Global.Orange : Global.GrayColor)
            .style("stroke", "black")
            .style("stroke-width", 0)
            .style("stroke-opacity", 1);
        
        grid_groups.append("rect")
            .attr("class", "display")
            .attr("x", 0.5 * that.boundingbox_width)
            .attr("y", 0.5 * that.boundingbox_width)
            .attr("width", d => d.width - that.boundingbox_width)
            .attr("height", d => d.width - that.boundingbox_width)
            .style("fill", d => d.mismatch > 0 ? Global.Orange : Global.GrayColor)
            .style("pointer-events", "none");
    }

    this.update = function(){
        that.set_update();
        that.grid_update();
    }

    this.set_update = function(){
        that.e_sets
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr(
                "transform",
                (d) => "translate(" + d.x + ", " + d.y + ")"
            )
        
        that.e_sets.select("rect.background")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("height", d => d.height);

        that.e_sets.selectAll("g.detection-result")
            .select("image")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            // .attr("height", d => that.get_expand_set_id() === -1 ? d.vis_h : 0);
            .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
            .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");
        
        that.e_sets.selectAll("g.detection-result")
            .selectAll("rect.box")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
            .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");

        that.e_sets.select(".expand-path")
            .attr("d", d => d.id === that.get_expand_set_id() ? 
                Global.minus_path_d(-11, 0, 10, 10, 2): Global.plus_path_d(-11, 0, 10, 10, 2))
    };

    this.grid_update = function(){

    }

    this.remove = function(){
        that.set_remove();
        that.grid_remove();
    }   

    this.set_remove = function(){
        that.e_sets
        .exit()
        .transition()
        .duration(that.remove_ani)
        .style("opacity", 0)
        .remove();
    };

    that.grid_remove = function(){

    }

    that.set_mode = function(mode){
        console.log("set mode", mode);
        that.mode = mode;
        if (mode === "cropping") {
            d3.select("#cropping").select("path").attr("d", Global.d_rollback);
            d3.select("#selecting").select("path").attr("d", Global.d_select);
            that.enter_overview();
        } else if (mode === "selecting") {
            d3.select("#selecting").select("path").attr("d", Global.d_rollback);
            d3.select("#cropping").select("path").attr("d", Global.d_scan);
            that.enter_overview();
        } else if (mode === "exploring") {
            d3.select("#cropping").select("path").attr("d", Global.d_scan);
            d3.select("#selecting").select("path").attr("d", Global.d_select);
            that.quit_overview();
        }
    }

    that.get_mode = function(){
        return that.mode;
    }

    that.enter_overview = function(){
        that.overview_group.select("#overview-1")
            .attr("x", offset_x)
            .attr("y", offset_y)
            .attr("width", plot_width)
            .attr("height", plot_height);
        // that.overview_group.select("#overview-2")
        //     .attr("x", small_x_2)
        //     .attr("y", small_y_2)
        //     .attr("width", small_grid_width)
        //     .attr("height", small_grid_width);
        that.overview_group.style("visibility", "visible");
        that.overview_group.select("#viewbox").style("visibility", "hidden");
        that.confirm_button.style("visibility", "hidden");
    }

    that.quit_overview = function(){
        that.overview_group.style("visibility", "hidden");
        that.overview_group.select("#viewbox").style("visibility", "hidden");
        that.confirm_button.select("#confirm-resample").style("visibility", "hidden");

    }

    that._init = function(){
        that.overview_group = that.parent.svg
            .append("g")
            .attr("id", "overview-group");

        that.overview_group.attr("transform",
            "translate(" + ( 0 ) + "," + ( that.text_height )+ ")")
            .style("visibility", "hidden");
        that.overview_group.append("rect")
            .attr("id", "overview-1")
            .attr("class", "overview-box");
        // that.overview_group.append("rect")
        //     .attr("id", "overview-2")
        //     .attr("class", "overview-box");
        that.overview_group.selectAll(".overview-box")
            .attr("x", 0)
            .attr("y", 0)
            .style("fill", "white")
            .style("stroke", "grey")
            .style("stroke-width", 5)
            .style("opacity", 0.3);
        that.overview_group.append("rect")
            .attr("id", "viewbox")
            .style("stroke-dasharray", "5, 5")
            .style("fill", "white")
            .style("stroke", "grey")
            .style("stroke-width", 5)
            .style("opacity", 0.5);

        d3.select("#cropping").on('click', function() {
            var mode = d3.select(this).select("path").attr("d") === Global.d_scan ? 
                "cropping" : "exploring";
            that.set_mode(mode);
        });
        
        d3.select("#selecting").on('click', function() {
            var mode = d3.select(this).select("path").attr("d") === Global.d_select ? 
                "selecting" : "exploring";
            that.set_mode(mode);
        });

        function adjust_sampling_area(area) {
            relative_sampling_area = area;
            // console.log("relative_sampling are", relative_sampling_area);
            that.overview_group.select("#viewbox")
                .attr("x", relative_sampling_area.x * plot_width + offset_x)
                .attr("y", relative_sampling_area.y * plot_height + offset_y - that.text_height)
                .attr("width", relative_sampling_area.w * plot_width)
                .attr("height", relative_sampling_area.h * plot_height);
        }
        function compute_viewbox(x1, y1, x2, y2) {
            var min_x = Math.min(x1, x2), max_x = Math.max(x1, x2),
                min_y = Math.min(y1, y2), max_y = Math.max(y1, y2);
            var new_area = {
                x: (min_x - plot_x) / plot_width,
                y: (min_y - plot_y) / plot_height,
                w: (max_x - min_x) / plot_width,
                h: (max_y - min_y) / plot_height
            };
            if (new_area.x + new_area.w > 1 && new_area.x < 1) {
                return relative_sampling_area;
            } else {
                return new_area;
            }
        }

        that.overview_group.on("mousedown", function(ev){
            // var offset = $(d3.select(this).node()).offset();
            plot_x = offset_x;
            plot_y = offset_y;
            mouse_pos = {
                x: ev.offsetX,
                y: ev.offsetY
            };
            mouse_pressed = d3.select(this).attr("id");
            that.overview_group.select("#viewbox").style("visibility", "visible");
            that.confirm_button.style("visibility", "hidden");
            adjust_sampling_area(compute_viewbox(mouse_pos.x, mouse_pos.y, mouse_pos.x, mouse_pos.y));
        })
        .on("mousemove", function(ev) {
            if (!mouse_pressed) {
                return;
            }
            
            adjust_sampling_area(compute_viewbox(mouse_pos.x, mouse_pos.y, ev.offsetX, ev.offsetY));

            // let left_x = relative_sampling_area.x;
            // let top_y = relative_sampling_area.y;
            // let right_x = left_x + relative_sampling_area.w;
            // let bottom_y = top_y + relative_sampling_area.h;

            // if (parent.get_mode() === "selecting") {
            //     if (parent.get_position_mode() !== "juxtaposition") {
            //         // TODO: selected data
            //     }
            // }
        })
        .on("mouseup", function(ev) {
            if (!mouse_pressed) {
                return;
            }
            mouse_pressed = false;
            adjust_sampling_area(compute_viewbox(mouse_pos.x, mouse_pos.y, ev.offsetX, ev.offsetY));
            let button_x = (relative_sampling_area.x + relative_sampling_area.w) 
                * plot_width + margin_size + offset_x;
            let button_y = (relative_sampling_area.y + relative_sampling_area.h) * plot_width  
                + margin_top_size + that.text_height;
            that.confirm_button.attr("transform",
                "translate(" + button_x + ", " + button_y + ")")
                .style("visibility", "visible");
        });


        that.confirm_button = that.parent.svg.append("g")
            .attr("id", "confirm-resample")
            .style("visibility", "hidden");
        that.confirm_button.append("circle")
            .attr("r", 20)
            .attr("fill", "grey");
        that.confirm_button.append("text")
            .attr("class", 'glyphicon')
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle")
            .attr('dy', '0.25em')
            .style("fill", "white")
            .style("opacity", 1)
            .style('font-size', '20px')
            .style('cursor', 'hand')
            .text('\ue015');

        that.confirm_button.on("click", function(ev) {
            console.log("confirm buttom click");
            if (that.get_mode() === "cropping") {
                // sampling_area = {
                //     x: sampling_area.x + sampling_area.w * relative_sampling_area.x,
                //     y: sampling_area.y + sampling_area.h * relative_sampling_area.y,
                //     w: sampling_area.w * relative_sampling_area.w,
                //     h: sampling_area.h * relative_sampling_area.h
                // };
                // that.resample();
            } else if (that.get_mode() === "selecting") {
                // let selected_items_id = [];
                // for (let i = 0; i < train_data.length; i++) {
                //     if (train_data[i].selected === true) {
                //         selected_items_id.push(train_data[i].get_id());
                //     }
                // }
                // for (let i = 0; i < test_data.length; i++) {
                //     if (test_data[i].selected === true) {
                //         selected_items_id.push(test_data[i].get_id());
                //     }
                // }
            }
            that.set_mode("exploring");
            d3.select(this).style("visibility", "hidden");
            ev.stopPropagation();
        });
    }.call()

}

export default ImageCards;