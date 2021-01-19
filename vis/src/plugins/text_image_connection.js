import * as d3 from "d3";
import * as Global from "../plugins/global";
const TextImageConnection = function (parent) {
    let that = this;
    that.parent = parent;

    that.set_link_group = that.parent.set_link_group;

    // animation
    that.create_ani = that.parent.create_ani;
    that.update_ani = that.parent.update_ani;
    that.remove_ani = that.parent.remove_ani;

    that.sub_component_update = function (set_links) {
        // update state

        // update view
        that.e_set_links = that.set_link_group
            .selectAll(".set-link")
            .data(set_links, d => d.source.id + "-" + d.target.id); 

        that.create();
        that.update();
        that.remove();
    }

    that.create = function () {
        // set links
        that.e_set_links
            .enter()
            .append("path")
            .attr("class", "set-link")
            .attr("id", d => d.source.id + "-" + d.target.id)
            // .attr("d", Global.set_line)
            .attr(
                "d",
                d3.linkHorizontal()
                    .x((d) => d.x)
                    .y((d) => d.y)
            )
            .style("opacity", 0)
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 0.5)
            // .style("stroke-dasharray", "5, 5")
            .transition()
            .duration(that.create_ani)
            .delay(that.update_ani + that.remove_ani)
            .style("opacity", 1);
    };

    that.update = function () {
        that.e_set_links
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("d", 
            d3.linkHorizontal()
                .x((d) => d.x)
                .y((d) => d.y));
    };

    that.remove = function () {
        that.e_set_links
            .exit()
            .transition()
            .duration(that.remove_ani)
            .style("opacity", 0)
            .remove();

    };

}

export default TextImageConnection;