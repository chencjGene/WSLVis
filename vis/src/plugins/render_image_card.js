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

    this.sub_component_update = function(sets) {
        // update layout config
        this.get_set_layout_from_parent();

        // update state 
        console.log("image card sub component update", sets);

        // update view
        this.e_sets = this.set_group.selectAll(".set").data(sets, d => d.type); 

        this.remove();
        this.update();
        this.create();
    };

    this.create = function() {
        // set
        let set_groups = this.e_sets
            .enter()
            .append("g")
            .attr("class", "set")
            .attr("id", d => d.type)
            .attr(
                "transform",
                (d) => "translate(" + d.x + ", " + d.y + ")"
            );

        set_groups
            .append("rect")
            .attr("class", "background")
            .style("fill", "white")
            .style("stroke", "#f0f0f0")
            .style("stroke-width", 1)
            .style("opacity", 0)
            .attr("width", (d) => d.width)
            .attr("height", (d) => d.height)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
        
        // that.image_groups = set_groups.selectAll("g.detection-result")
        //     .data(d => d.vis_image);
        // that.image_groups.enter()
        //     .append("g")
        //     .attr("class", "detection-result")
        //     .attr(
        //         "transform",
        //         (d) => "translate(" + d.x + ", " + that.image_margin / 2 + ")"
        //     );
        
        // e_image_groups.append("image")
        //     .attr("x", 0)
        //     .attr("y", 0)
        //     .attr("width", d => d.vis_w)
        //     .attr("height", d => d.vis_h)
        //     .attr("href", d => that.server_url + `/image/image?filename=${d.idx}.jpg`);
        
        // that.box_groups = e_image_groups.selectAll("rect.box")
        //     .data(d => {
        //         let dets = d.d;
        //         let res = [];
        //         for (let i = 0; i < dets.length; i++){
        //             let x = d.vis_w * dets[i][0];
        //             let width = d.vis_w * (dets[i][2] - dets[i][0]);
        //             let y = d.vis_h * dets[i][1];
        //             let height = d.vis_h * (dets[i][3] - dets[i][1]);
        //             res.push({x, y, width, height});
        //         }
        //         return res;
        //     });
        // that.box_groups.enter()
        //     .append("rect")
        //     .attr("rect", "box")
        //     .attr("x", d => d.x)
        //     .attr("y", d => d.y)
        //     .attr("width", d => d.width)
        //     .attr("height", d => d.height)
        //     .style("fill", "none")
        //     .style("stroke", "green")
        //     .style("stroke-width", 1);

            
    };

    this.update = function(){
        this.e_sets
        .transition()
        .duration(that.update_ani)
        .delay(that.remove_ani)
        .attr(
            "transform",
            (d) => "translate(" + d.x + ", " + d.y + ")"
        );
    };

    this.remove = function(){

        this.e_sets
        .exit()
        .transition()
        .duration(this.remove_ani)
        .style("opacity", 0)
        .remove();
    };

}

export default ImageCards;