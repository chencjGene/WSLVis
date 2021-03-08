import * as Global from "../plugins/global";

const ImageCards = function(parent){
    let that =this;
    that.parent = parent;
    
    that.set_group = that.parent.set_group;

    that.server_url = that.parent.server_url;


    // animation
    that.create_ani = that.parent.create_ani;
    that.update_ani = that.parent.update_ani;
    that.remove_ani = that.parent.remove_ani;

    this.get_set_layout_from_parent = function(){
        // set
        that.layout_height = that.parent.layout_height;
        that.set_height = that.parent.set_height;
        that.set_left = that.parent.set_left;
        that.set_width = that.parent.set_width;
        that.set_margin = that.parent.set_margin;
        that.image_height = that.parent.image_height;
        that.image_margin = that.parent.image_margin;
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

    this.sub_component_update = function(sets, vis_image_per_cluster) {
        // update layout config
        that.get_set_layout_from_parent();

        // update state 
        that.vis_image_per_cluster = vis_image_per_cluster;
        Object.values(that.vis_image_per_cluster).forEach(d => {
            let x = that.image_margin;
            d.forEach(n => {
                n.vis_h = that.image_height;
                n.vis_w = that.image_height;
                n.x = x;
                x = x + n.vis_w + that.image_margin;
            })
        })
        console.log("image card sub component update", sets, that.detections);
        

        // update view
        that.e_sets = that.set_group.selectAll(".set").data(sets, d => d.id); 

        that.remove();
        that.update();
        that.create();
    };

    this.create = function() {
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
            .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");

            
    };

    this.update = function(){
        that.e_sets
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr(
                "transform",
                (d) => "translate(" + d.x + ", " + d.y + ")"
            );
        
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

    this.remove = function(){

        that.e_sets
        .exit()
        .transition()
        .duration(that.remove_ani)
        .style("opacity", 0)
        .remove();
    };

}

export default ImageCards;