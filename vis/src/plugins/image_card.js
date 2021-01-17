const ImageCards = function(parent){
    let that =this;
    that.parent = parent;
    
    that.set_group = that.parent.set_group;

    that.server_url = that.parent.server_url;

    // set
    that.set_height = that.parent.set_height;
    that.set_left = that.parent.set_left;
    that.set_width = that.parent.set_width;
    that.set_margin = that.parent.set_margin;


    // animation
    that.create_ani = that.parent.create_ani;
    that.update_ani = that.parent.update_ani;
    that.remove_ani = that.parent.remove_ani;

    this.sub_component_update = function(sets) {
        // update state 
        console.log("image card sub component update", sets);

        // update view
        this.e_sets = this.set_group.selectAll(".set").data(sets, d => d.type); //TODO: id map

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
        
        that.image_groups = set_groups.selectAll("g.detection-result")
            .data(d => d.selected_image);
        let e_image_groups = that.image_groups.enter()
            .append("g")
            .attr("class", "detection-result")
            .attr(
                "transform",
                (d, i) => "translate(" + (i * that.set_height) + ", " + 0 + ")"
            );
        e_image_groups.append("image")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", that.set_height)
            .attr("height", that.set_height)
            .attr("href", d => that.server_url + `/image/image?filename=${d.idx}.jpg`);
            
    };

    this.update = function(){

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