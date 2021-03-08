// import * as d3 from "d3";
import * as Global from "./global";
import { exit_type } from "./layout_text";

const TextTree = function (parent) {
    let that = this;
    that.parent = parent;

    that.tree_node_group = that.parent.tree_node_group;
    that.rest_node_group = that.parent.rest_node_group;
    
    // text position
    that.text_height = that.parent.text_height;
    
    // node width
    that.max_text_width = that.parent.max_text_width;
    
    // detection result layout
    that.layout_width = that.parent.layout_width;
    that.layout_height = that.parent.layout_height;
    that.node_width = that.parent.node_width;
    that.layer_height = that.parent.layer_height;

    // bar size 
    that.bar_width = that.parent.bar_width;
    that.bar_height = that.parent.bar_height;
    that.rounded_r = that.parent.rounded_r;


    that.change_selected_flag = function(d, flag){
        console.log("change selected flag", d.selected_flag, flag);
        that.create_ani = 0;
        that.remove_ani = 0;
        that.update_ani /= 2;
        d.selected_flag = flag;
        that.parent.set_selected_flag(that.parent.tree);
        console.log("change selected flag after", d.selected_flag, flag)
    }

    that.set_animation_time = function(){
        // animation
        that.create_ani = that.parent.create_ani;
        that.update_ani = that.parent.update_ani;
        that.remove_ani = that.parent.remove_ani;
    };
    that.set_animation_time();

    that.set_focus_node = function (nodes) {
        that.parent.set_focus_node(nodes);
    };

    that.fetch_word = function(query){
        that.parent.$store.dispatch("fetch_word", query);
    }

    that.set_selected_node = function(node){
        that.parent.set_selected_node(node);
    }

    that.sub_component_update = function (nodes, rest_nodes) {
        // update state
        that.tree_node_group_x = that.parent.tree_node_group_x;
        that.tree_node_group_y = that.parent.tree_node_group_y;
        that.expand_tree =that.parent.expand_tree;

        // update view
        that.e_nodes = that.tree_node_group
            .selectAll(".tree-node")
            .data(nodes, (d) => d.id);
        
        that.e_rest_nodes = that.rest_node_group
            .selectAll(".rest-tree-node")
            .data(rest_nodes, (d) => d.id);

        that.create();
        that.update();
        that.remove();

        that.set_animation_time();
    };

    that.create = function () {
        that.node_create();
        that.rest_node_create();
    };

    that.node_create = function () {
        // node circle
        let node_groups = that.e_nodes
            .enter()
            .append("g")
            .attr("class", "tree-node")
            .attr("id", (d) => "id-" + d.id)
            .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")");
        node_groups
            .transition()
            .duration(that.create_ani)
            .delay(that.remove_ani + that.update_ani)
            .style("opacity", 1);
        node_groups
            .append("title")
            .style("font-size", "18px")
            .text((d) => d.full_name);
        node_groups
            .append("rect")
            .attr("class", "background")
            .attr("rx", that.layer_height / 12)
            .attr("ry", that.layer_height / 12)
            .attr("x", that.layer_height / 4)
            .attr("y", (-that.layer_height * 0.8) / 2)
            .attr("height", that.layer_height * 0.8)
            .attr("width", () => {
                return that.max_text_width;
            })
            // TODO: 
            // .style("fill", d => d.selected_flag ? Global.DarkGray : "#EBEBF3")
            .style("fill", "#EBEBF3")
            .style("fill-opacity", 0)
            .on("mouseover", (ev, d) => {
                that.highlight(ev, d);
            })
            .on("mouseout", (ev, d) => {
                // that.hideTooltip();
                that.dehighlight(ev, d);
            })
            .on("click", (ev, d) => {
                console.log("on click tree node");
                // that.change_selected_flag(d, !d.selected_flag);

                // TODO: double click
                let query = {
                    tree_node_id: d.id,
                    match_type: "p",
                };
                that.fetch_word(query);
                let node = {
                    full_name: d.full_name
                };
                that.set_selected_node(node);
            })
            .transition()
            .duration(that.create_ani)
            .delay(that.remove_ani + that.update_ani)
            .style("fill-opacity", 1);

        // precision and recall
        let bars = node_groups
            .append("g")
            .attr("class", "node-bars")
            .attr(
                "transform",
                () =>
                    "translate(" +
                    (that.max_text_width - 15) +
                    ", " +
                    -(that.bar_height - that.rounded_r) / 2 +
                    ")"
            );
        let individual_bar = bars
            .selectAll("g.bar")
            .data((d) => {
                let precision = {
                    value: d.data.precision,
                    color: "#c982ce",
                    type: "precision",
                };
                let recall = {
                    value: d.data.recall,
                    color: "#4fa7ff",
                    type: "recall",
                };
                return [precision, recall];
            })
            .enter()
            .append("g")
            .attr("class", "bar")
            .attr(
                "transform",
                (_, i) => "translate(" + i * (that.bar_width + 3) + ", " + 0 + ")"
            );
        individual_bar
            .append("rect")
            .attr("class", "bar-background")
            .attr("rx", that.rounded_r)
            .attr("ry", that.rounded_r)
            .attr("width", that.bar_width)
            .attr("height", that.bar_height)
            .style("fill", "none")
            .style("stroke", (d) => d.color)
            .style("stroke-width", 1);

        individual_bar
            .append("rect")
            .attr("class", (d) => "bar-value bar-" + d.type)
            .attr("rx", that.rounded_r)
            .attr("ry", that.rounded_r)
            .attr("width", that.bar_width)
            .attr("height", that.bar_height)
            .style("fill", (d) => d.color)
            .style("clip-path", (d) => {
                return `inset(${(1 - d.value) * that.bar_height
                    }px ${0}px ${0}px ${0}px)`;
            });
        bars
            .style("opacity", 0)
            .transition()
            .duration(that.create_ani)
            .delay(that.remove_ani + that.update_ani)
            .style("opacity", 1);

        node_groups
            .append("path")
            .attr("class", (d) => "icon icon-" + d.type)
            .attr("d", function (d) {
                return Global.node_icon(0, 0, d.type);
            })
            .style("fill", Global.GrayColor)
            .style("opacity", 0)
            .transition()
            .duration(that.create_ani)
            .delay(that.update_ani + that.remove_ani)
            .style("opacity", () => (that.expand_tree ? 1 : 0));

        node_groups
            .append("rect")
            .attr("class", d => "icon-background icon-bg-" + d.type)
            .attr("x", -8)
            .attr("y", -8)
            .attr("width", 16)
            .attr("height", 16)
            .style("fill", "white")
            .style("opacity", 0)
            .on("mouseover", (ev, d) => {
                that.icon_highlight(ev, d);
            })
            .on("mouseout", (ev, d) => {
                that.icon_dehighlight(ev, d);
            })
            .on("click", (ev, d) => {
                console.log("click icon", d.type, d);
                if (!that.expand_tree) return;
                // if (d.type > 0) return;
                console.log("click tree node", d.name);
                // that.highlight(ev, d, "rgb(211, 211, 229)");
                that.set_focus_node([d]);
            });

        // node name
        node_groups
            .append("text")
            .attr("class", "node-name")
            .text((d) => {
                return d.name;
            })
            .attr("text-anchor", "start")
            .attr("x", that.layer_height / 2)
            .attr("font-size", "18px")
            .attr("dy", ".3em")
            .style("opacity", 0)
            .transition()
            .duration(that.create_ani)
            .delay(that.update_ani + that.remove_ani)
            .style("opacity", 1);
        // node link
        node_groups
            .append("path")
            .attr("class", "node-link")
            .attr("d", (d) => {
                return (
                    "M" +
                    d.link_x +
                    ", " +
                    d.link_top +
                    " L " +
                    d.link_x +
                    ", " +
                    d.link_bottom
                );
            })
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 0.5)
            .style("opacity", 0)
            .transition()
            .duration(that.create_ani)
            .delay(that.update_ani + that.remove_ani)
            .style("opacity", 1);
    };
    
    that.rest_node_create = function() {
        let node_groups = that.e_rest_nodes
            .enter()
            .append("g")
            .attr("class", "rest-tree-node")
            .attr("id", (d) => "id-" + d.id)
            .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")")
            .style("opacity", 0)
            .on("click", (ev, d) => {
                console.log("set focus node");
                that.set_focus_node(d.rest_children);
            });
        node_groups
            .append("path")
            .attr("class", "icon")
            .attr("d", Global.node_icon(0, 0, 0))
            .attr("fill", Global.GrayColor);
        node_groups
            .selectAll("rest-node-rect")
            .data((d) => {
                console.log("rest node groups data", d);
                return d.rest_children;
            })
            .enter()
            .append("rect")
            .attr("class", "rest-node-rect")
            .attr("rx", that.layer_height / 12)
            .attr("ry", that.layer_height / 12)
            .attr("x", (d) => that.layer_height / 4 + d.x_delta)
            .attr("y", (d) => d.y_delta)
            .attr("height", that.layer_height * 0.6)
            .attr("width", () => {
                return that.max_text_width;
            })
            .style("fill", (d) =>
                d.last_rest_children ? "#EBEBF3" : "rgb(211, 211, 229)"
            )
            .style("stroke", "white")
            .style("stroke-width", 1);
        node_groups
            .transition()
            .duration((d) => {
                if (d.prev_vis) {
                    // return that.remove_ani * 0.5;
                    return that.create_ani;
                } else {
                    return that.create_ani;
                }
            })
            .delay((d) => {
                if (d.prev_vis) {
                    // return that.remove_ani * 0.5 + that.remove_ani;
                    return that.remove_ani + that.update_ani;
                } else {
                    return that.remove_ani + that.update_ani;
                }
            })
            .style("opacity", 1);
    };

    that.update = function () {
        that.node_update();
        that.rest_node_update();
    };

    that.node_update = function () {
        that.tree_node_group
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("transform", () => {
                return (
                    "translate(" +
                    that.tree_node_group_x +
                    ", " +
                    that.tree_node_group_y +
                    ")"
                );
            });
        that.e_nodes
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")");
        that.e_nodes
            .select("rect.background")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("x", that.layer_height / 4)
            .attr("y", (-that.layer_height * 0.8) / 2)
            .attr("height", that.layer_height * 0.8)
            .attr("width", () => {
                // return Global.getTextWidth(d.data.name, "16px Roboto, sans-serif") + that.layer_height / 2;
                return that.max_text_width;
            })
            .style("fill", d => d.selected_flag ? Global.DarkGray : "#EBEBF3");

        if (that.focus_node) {
            that.tree_node_group
                .select("#id-" + that.focus_node[0].id)
                .select("rect.background")
                .transition()
                .duration(that.create_ani)
                .delay(that.remove_ani + that.update_ani + that.create_ani)
                .style("fill", "#EBEBF3");
        }

        that.e_nodes
            .select("path.icon")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("d", function (d) {
                return Global.node_icon(0, 0, d.type);
            })
            .style("opacity", () => (that.expand_tree ? 1 : 0))
            .style("fill", Global.GrayColor)
        that.e_nodes
            .select("rect.icon-background")
            .attr("class", d => "icon-background icon-bg-" + d.type);
        that.e_nodes
            .select("text")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .text((d) => d.name)
            .style("opacity", 1);
        that.e_nodes
            .select("path.node-link")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("d", (d) => {
                return (
                    "M" +
                    d.link_x +
                    ", " +
                    d.link_top +
                    " L " +
                    d.link_x +
                    ", " +
                    d.link_bottom
                );
            });

        that.e_nodes
            .select("g.node-bars")
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr(
                "transform",
                () =>
                    "translate(" +
                    (that.max_text_width - 15) +
                    ", " +
                    -(that.bar_height - that.rounded_r) / 2 +
                    ")"
            );
        that.e_nodes
            .select("g.node-bars")
            .selectAll("g.bar")
            .data((d) => {
                let precision = {
                    value: d.data.precision,
                    color: "#c982ce",
                    type: "precision",
                };
                let recall = {
                    value: d.data.recall,
                    color: "#4fa7ff",
                    type: "recall",
                };
                return [precision, recall];
            })
            .attr(
                "transform",
                (_, i) => "translate(" + i * (that.bar_width + 3) + ", " + 0 + ")"
            )
            .selectAll(".bar-value")
            .style("clip-path", (d) => {
                return `inset(${(1 - d.value) * that.bar_height
                    }px ${0}px ${0}px ${0}px)`;
            });
    };
    
    that.rest_node_update = function() {
        that.rest_node_group
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr("transform", () => {
                let x = that.layer_height / 2;
                if (!that.expand_tree) {
                    x = 0;
                }
                return (
                    "translate(" +
                    x +
                    ", " +
                    (that.text_height + that.layer_height / 2) +
                    ")"
                );
            });
        that.e_rest_nodes
            .transition()
            .duration(that.update_ani)
            .delay(that.remove_ani)
            .attr(
                "transform",
                (d) => "translate(" + d.x + ", " + d.y + ")"
            );
        that.e_rest_nodes
            .selectAll("rest-node-rect")
            .attr("y", (d, i) => (-that.layer_height * 0.8) / 2 + i * 10)
            .attr("width", () => {
                return that.max_text_width;
            });
    };

    that.remove = function () {
        that.node_remove();
        that.rest_node_remove();
    };

    that.node_remove = function () {
        that.e_nodes.exit().attr("", d => {
            let [type, translate] = exit_type(d);
            d.exit_type = type;
            d.translate = translate;
            d.exit_duration = d.exit_type > 1 ? that.update_ani : that.remove_ani;
            d.exit_delay = d.exit_type > 1 ? that.remove_ani : 0;
        })
        that.e_nodes
            .exit()
            .transition()
            .duration(d => d.exit_duration)
            .delay(d => d.exit_delay)
            .attr("transform", d => d.translate + " scale(1, 0)")
            .style("opacity", 0)
            .remove();
    };
    
    that.rest_node_remove = function() {
        that.e_rest_nodes.exit().attr("", (d) => {
            let [type, translate] = exit_type(d.parent);
            d.exit_type = type;
            d.translate = translate;
            d.exit_duration =
                d.exit_type > 1 ? that.update_ani : that.remove_ani;
            d.exit_delay = d.exit_type > 1 ? that.remove_ani : 0;
            console.log(
                "rest_node_remove",
                d.exit_type,
                d.exit_duration,
                d.exit_delay,
                d.translate
            );
        });
        that.e_rest_nodes
            .exit()
            .transition()
            .duration((d) => d.exit_duration)
            .delay((d) => d.exit_delay)
            .attr("transform", (d) => d.translate + " scale(1, 0)")
            .style("opacity", 0)
            .remove();
    };

    // that.highlight = function(ev, d, color) {
    that.highlight = function() {
        // console.log("highlight in tree");
        // color = color || "#E0E0EC";
        // that.tree_node_group
        //     .select("#id-" + d.id)
        //     .select("rect.background")
        //     .style("fill", color);
    };
    
    // that.dehighlight = function(ev, d) {
    that.dehighlight = function() {
        // that.tree_node_group
        //     .select("#id-" + d.id)
        //     .select("rect.background")
        //     .style("fill", d => d.selected_flag ? Global.DarkGray : "#EBEBF3");
    };

    that.icon_highlight = function(ev, d) {
        console.log("icon-highlight");
        // if (d.type > 0) return;
        that.tree_node_group
            .select("#id-" + d.id)
            .select("path.icon")
            .style("fill", "#1f1f1f");
    };

    that.icon_dehighlight = function(ev, d) {
        that.tree_node_group
            .select("#id-" + d.id)
            .select("path.icon")
            .style("fill", Global.GrayColor
            );
    };

}

export default TextTree;