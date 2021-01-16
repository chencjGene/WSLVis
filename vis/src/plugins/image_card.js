const ImageCards = function(parent){
    let that =this;
    that.parent = parent;
    
    that.set_group = that.parent.set_group;

    // animation
    that.create_ani = that.parent.create_ani;
    that.update_ani = that.parent.update_ani;
    that.remove_ani = that.parent.remove_ani;
    
    this.sub_component_update = function(sets) {
        // update state 

        // update view
        this.e_sets = this.set_group.selectAll(".set").data(sets); //TODO: id map

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