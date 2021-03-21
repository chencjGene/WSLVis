<template>
    <v-col cols="9" class="main-view fill-height">
        <info-tooltip
            :left="tooltip.left"
            :top="tooltip.top"
            :width="tooltip.width"
            :show="tooltip.show"
            :content="tooltip.content"
        >
        </info-tooltip>
        <v-col cols="12" class="main-content pa-0"> 
            <!-- <div style="position: absolute; padding-left: 600px; padding-top: 3px" >
                <div id="cropping" class="waves-effect waves-light btn-floating grey" title="Zoom in">
                    <svg class="icon" width="24px" height="24px" transform="translate(2.6, 2.6)" viewBox="0 0 1024 1024">
                        <path fill="white" d="M136 384h56c4.4 0 8-3.6 8-8V200h176c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H196c-37.6 0-68 30.4-68 68v180c0 4.4 3.6 8 8 8zM648 200h176v176c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8V196c0-37.6-30.4-68-68-68H648c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zM376 824H200V648c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v180c0 37.6 30.4 68 68 68h180c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM888 640h-56c-4.4 0-8 3.6-8 8v176H648c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h180c37.6 0 68-30.4 68-68V648c0-4.4-3.6-8-8-8zM904 476H120c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8z" />
                    </svg>
                </div>
                <div  style="margin-left: 3px" id="selecting" class="waves-effect waves-light btn-floating grey" title="Select">
                    <svg class="icon" width="24px" height="24px" transform="translate(2.6, 2.6)"  viewBox="0 0 1024 1024">
                        <path fill="white" d="M880 112H144c-17.7 0-32 14.3-32 32v736c0 17.7 14.3 32 32 32h360c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H184V184h656v320c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8V144c0-17.7-14.3-32-32-32zM653.3 599.4l52.2-52.2c4.7-4.7 1.9-12.8-4.7-13.6l-179.4-21c-5.1-0.6-9.5 3.7-8.9 8.9l21 179.4c0.8 6.6 8.9 9.4 13.6 4.7l52.4-52.4 256.2 256.2c3.1 3.1 8.2 3.1 11.3 0l42.4-42.4c3.1-3.1 3.1-8.2 0-11.3L653.3 599.4z" />
                    </svg>
                </div>
            </div> -->
        </v-col>
    </v-col>
</template>

<script>
/*
* this components calls all computation components (treecut, set_managers, etc.)
* to get elements positions and other attributions,
* and call all rendering components (text_tree, image_card, etc.)
* to render all elements.
*/

// import Vue from "vue"
import { mapActions, mapState, mapMutations } from "vuex";
import * as d3 from "d3";  
import * as Global from "../plugins/global";
import "../assets/font.css"

// computation components
import {
    mini_tree_layout,
    TreeCut,
    tree_layout,
} from "../plugins/layout_text";
import {image_cluster_list_layout} from "../plugins/layout_image";
import {ConnectionLayout} from "../plugins/layout_connection";

// import { SetManager } from "../plugins/set_manager";

// render components
import TextTree from "../plugins/render_text_tree";
import TextImageConnection from "../plugins/render_connection";
import ImageCards from "../plugins/render_image_card";

import InfoTooltip from "../components/infotooltip";
export default {
    name: "Detection",
    components: {
        InfoTooltip: InfoTooltip,
    },
    data: () => ({
        bbox_width: null,
        bbox_height: null,
        layout_width: null,
        layout_height: null,
        top_padding: null,
        nodes: null,
        links: null,
    }),
    computed: {
        ...mapState([
            "tree",
            "use_treecut",
            "f1_score_selected",
            "image_cluster_list",
            "vis_image_per_cluster",
            "cluster_association_mat",
            "mismatch",
            "all_sets",
            "focus_node",
            "selected_node",
            "expand_tree",
            "expand_set_id",
            "grid_data",
            "nav_id",
            "tooltip",
            "server_url",
            "selected_flag"
        ]),
        // selected_flag(){
        //     return this.tree.all_descendants.map(d => !! d.selected_flag);
        // }
    },
    methods: {
        ...mapActions(["fetch_hypergraph", "fetch_word", "fetch_image", "fetch_grid_layout"]),
        ...mapMutations([
            "set_selected_flag",
            "set_focus_node",
            "set_selected_node",
            "set_focus_image",
            "set_expand_tree",
            "set_expand_set_id",
            "showTooltip",
            "hideTooltip",
            "set_words",
            "set_grid_layout_data",
            "set_use_treecut",
            "set_f1_score_selected"
        ]),
        treecut() {
            console.log("detection treecut");
            console.log("before treecut", this.tree);
            if (this.use_treecut){
                // tree position backup
                this.tree.all_descendants.forEach((d) => {
                    d.prev_x = d.x;
                    d.prev_y = d.y;
                    d.prev_vis = false;
                });
                this.tree.descendants().forEach((d) => (d.prev_vis = true));
                this.offset = this.treecut_class.treeCut(
                    this.focus_node,
                    this.tree,
                    this.tree_layout.layout_with_rest_node
                );
                this.tree.all_descendants.map((d) => (d.api = 0));
                this.offset = 0;
                this.tree.sort(function (a, b) {
                    return a.siblings_id - b.siblings_id;
                });
                console.log("after treecut", this.tree);
            }
            else{
                if (!this.focus_node) {
                    this.tree.children = this.tree.all_children;
                }
                else if(this.focus_node[0].type == 0){
                    this.focus_node[0].children = this.focus_node[0].all_children;
                }
                else if (this.focus_node[0].type == 1){
                    this.focus_node[0].children = [];
                }
                this.tree.descendants().forEach(d => {
                    d.beforeList = [];
                    d.afterList = [];
                })
            }
        },
        update_data() {
            console.log("detection update data");
            console.log(this.tree, this.image_cluster_list);

            // tree layout
            this.nodes = this.tree_layout.layout_with_rest_node(
                this.tree,
                this.expand_tree
            );
            this.rest_nodes = this.nodes.filter((d) => d.is_rest_node);
            this.nodes = this.nodes.filter((d) => !d.is_rest_node);
            this.tree_node_group_x = this.expand_tree
                ? this.layer_height / 2
                : 0;
            this.tree_node_group_y = this.text_height + this.layer_height / 2;
            this.leaf_nodes = this.nodes.filter((d) => d.children.length === 0);
            // this.leaf_nodes.forEach(d => {
            //     if (d.selected_flag===undefined) d.selected_flag = true;
            // });
            // this.selected_nodes = this.nodes.filter(d => d.selected_flag);

            // minitree layout
            let mat = this.mini_tree_layout.layout(this.tree);
            this.mini_nodes = mat.nodes;
            this.mini_links = mat.links;
            
            // update cut cluster association matrix
            this.connection_layout.update(this.leaf_nodes, this.image_cluster_list);

            // set layout
            console.log("selected_nodes", this.selected_nodes);
            // this.sets = this.connection_layout.reorder(this.image_cluster_list);
            [this.sets, this.grids, this.grid_pos] = this.image_layout.layout(this.image_cluster_list);

            this.set_links = this.connection_layout.get_links(this.sets);
        },
        update_view() {
            console.log("detection update view");

            this.text_tree_view.sub_component_update(this.nodes, this.rest_nodes);
            this.image_view.sub_component_update(this.sets, 
                this.vis_image_per_cluster, this.grids, this.grid_pos);
            this.connection_view.sub_component_update(this.set_links);

            this.e_mini_nodes = this.mini_tree_node_group
                .selectAll(".mini-tree-node")
                .data(this.mini_nodes, (d) => d.id);
            this.e_mini_links = this.mini_tree_link_group
                .selectAll(".mini-tree-link")
                .data(this.mini_links);
            this.e_shadow_links = this.mini_shadow_link_group
                .selectAll(".mini-highlight")
                .data(this.mini_links);

            this.remove();
            this.update();
            this.create();
        },
        create() {
            console.log("Global", Global.GrayColor, Global.Animation);
            this.expand_icon_create();
            // this.mini_create();
        },

        mini_create() {
            this.e_mini_nodes
                .enter()
                .append("circle")
                .attr("class", "mini-tree-node")
                .attr("id", (d) => "mini-id-" + d.id)
                .attr("r", 0.5)
                .attr("cx", (d) => d.mini_y)
                .attr("cy", (d) => d.mini_x)
                .style("fill-opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("fill-opacity", 1);
            this.e_mini_links
                .enter()
                .append("path")
                .attr("class", "mini-tree-link")
                .attr(
                    "d",
                    d3
                        .linkHorizontal()
                        .x((d) => d.mini_y)
                        .y((d) => d.mini_x)
                )
                .style("opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", 1);
            this.e_shadow_links
                .enter()
                .append("path")
                .attr("class", "mini-highlight")
                .attr(
                    "d",
                    d3
                        .linkHorizontal()
                        .x((d) => d.mini_y)
                        .y((d) => d.mini_x)
                )
                .style("opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", (d) => (d.target.mini_selected ? 1 : 0));
        },
        legend_create() {
            let that = this;
            let scale = 0.8;
            let top_y = 4;
            let bottom_y = 22;
            // this.svg
            //     .append("text")
            //     .attr("class", "topname")
            //     .attr("x", this.layer_height / 2)
            //     .attr("y", this.text_height / 3 + 1)
            //     .text("Category labels");
            // this.svg
            //     .append("text")
            //     .attr("class", "topname")
            //     .attr("x", this.set_left * 1.05)
            //     .attr("y", this.text_height / 3 + 1)
            //     .text("Detection results");

            this.svg
                .append("rect")
                .attr("class", "treecut-rect")
                .attr("x", 5)
                .attr("y", 20)
                .attr("rx", 4)
                .attr("ry", 4)
                .attr("width", 167)
                .attr("height", 16)
                .style("fill", "none")
                .style("stroke-width", 1)
                .style("stroke", Global.GrayColor)
                .style("pointer-event", "none");

            let checkbox = this.svg
                .append("g")
                .attr("class", "current-label-checkbox")
                .attr("transform", "translate("+ 
                    (45)+","+
                    (top_y)+")" + "scale(" + 1+"," + 1+")")
                .on("click", function() {
                    console.log("click tree cut", that.use_treecut);
                    if (that.use_treecut){
                        that.set_use_treecut(false);
                        d3.select(this).select("rect")
                            .attr("fill", "white");
                        d3.selectAll(".prec-rec-checkbox")
                            .select("rect")
                            .attr("fill", "white");
                        d3.selectAll(".mismatch-checkbox")
                            .select("rect")
                            .attr("fill", "white");
                    }
                    else{
                        that.set_use_treecut(true);
                        d3.select(this).select("rect")
                            .attr("fill", Global.GrayColor);
                        d3.selectAll(".prec-rec-checkbox")
                            .select("rect")
                            .attr("fill", that.f1_score_selected ? Global.GrayColor : "white")
                        d3.selectAll(".mismatch-checkbox")
                            .select("rect")
                            .attr("fill", that.f1_score_selected ? "white" : Global.GrayColor)
                    }
                });
            
            let prec_rec_checkbox = this.svg
                .append("g")
                .attr("class", "prec-rec-checkbox")
                .attr("transform", "translate("+ 
                    (10)+","+
                    (bottom_y)+")"+ "scale(" + scale+"," + scale+")")
                .on("click", function() {
                    console.log("click prec-rec-checkbox", that.f1_score_selected);
                    if (that.use_treecut && !that.f1_score_selected){
                        that.set_f1_score_selected(true);
                        d3.select(this).select("rect")
                            .attr("fill", Global.GrayColor);
                        d3.selectAll(".mismatch-checkbox")
                            .select("rect")
                            .attr("fill", "white");
                    }
                });

            let mismatch_checkbox = this.svg
                .append("g")
                .attr("class", "mismatch-checkbox")
                .attr("transform", "translate("+ 
                    (90)+","+
                    (bottom_y)+")"+ "scale(" + scale+"," + scale+")")
                .on("click", function() {
                    console.log("click prec-rec-checkbox", that.f1_score_selected);
                    if (that.use_treecut && that.f1_score_selected){
                        that.set_f1_score_selected(false);
                        d3.select(this).select("rect")
                            .attr("fill", Global.GrayColor);
                        d3.selectAll(".prec-rec-checkbox")
                            .select("rect")
                            .attr("fill", "white");
                    }
                });

            checkbox.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 14)
                .attr("height", 14)
                .attr("rx", 3.5)
                .attr("ry", 3.5)
                .attr("fill", Global.GrayColor)
                .attr("stroke", Global.GrayColor);
            checkbox.append("text")
                .style("stroke", "white")
                .style("fill", "white")
                .attr("text-anchor", "middle")
                .attr("font-size", "12px")
                .attr("x", 14 / 2)
                .attr("y", 14 / 2 + 5)
                .text("\u2714")
            checkbox.append("text")
                .attr("text-anchor", "start")
                .attr("x", 14 + 2)
                .attr("y", 12)
                .attr("font-size", "18px")
                .text("Treecut");

            prec_rec_checkbox.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 14)
                .attr("height", 14)
                .attr("rx", 3.5)
                .attr("ry", 3.5)
                .attr("fill", that.f1_score_selected ? Global.GrayColor : "white")
                .attr("stroke", Global.GrayColor);
            prec_rec_checkbox.append("text")
                .style("stroke", "white")
                .style("fill", "white")
                .attr("text-anchor", "middle")
                .attr("font-size", "12px")
                .attr("x", 14 / 2)
                .attr("y", 14 / 2 + 5)
                .text("\u2714")
            prec_rec_checkbox.append("text")
                .attr("text-anchor", "start")
                .attr("x", 14 + 2)
                .attr("y", 12)
                .attr("font-size", "18px")
                .text("F1 score");
            mismatch_checkbox.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", 14)
                .attr("height", 14)
                .attr("rx", 3.5)
                .attr("ry", 3.5)
                .attr("fill", that.f1_score_selected ? "white" : Global.GrayColor)
                .attr("stroke", Global.GrayColor);
            mismatch_checkbox.append("text")
                .style("stroke", "white")
                .style("fill", "white")
                .attr("text-anchor", "middle")
                .attr("font-size", "12px")
                .attr("x", 14 / 2)
                .attr("y", 14 / 2 + 5)
                .text("\u2714")
            mismatch_checkbox.append("text")
                .attr("text-anchor", "start")
                .attr("x", 14 + 2)
                .attr("y", 12)
                .attr("font-size", "18px")
                .text("Mismatch");
            
        },
        expand_icon_create() {
            // this.expanded_icon_group.on("click", () => {
            //     console.log("click expanded icon", this.expand_tree);
            //     this.set_expand_tree(!this.expand_tree);
            // });
            // this.expanded_icon_group
            //     .selectAll("rect")
            //     .data([this.expand_tree])
            //     .enter()
            //     .append("rect")
            //     .attr("width", 10)
            //     .attr("height", 10)
            //     .style("rx", 3)
            //     .style("ry", 3)
            //     .style("fill", "white")
            //     .style("stroke", "gray")
            //     .style("stroke-width", 1);
            // this.expanded_icon_group
            //     .selectAll("path")
            //     .data([this.expand_tree])
            //     .enter()
            //     .append("path")
            //     .style("stroke", "none")
            //     .style("fill", "gray")
            //     .attr("d", () => {
            //         if (this.expand_tree) {
            //             return Global.minus_path_d(0, 0, 10, 10, 2);
            //         } else {
            //             return Global.plus_path_d(0, 0, 10, 10, 2);
            //         }
            //     });
        },
        update() {
            this.expand_icon_update();
            // this.mini_update();
        },
        mini_update() {
            this.e_mini_nodes
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("cx", (d) => d.mini_y)
                .attr("cy", (d) => d.mini_x);
            this.e_mini_links
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr(
                    "d",
                    d3.linkHorizontal()
                        .x((d) => d.mini_y)
                        .y((d) => d.mini_x)
                );
            this.e_shadow_links
                .transition()
                .duration((d) =>
                    d.target.mini_selected ? this.create_ani : this.update_ani
                )
                .delay((d) =>
                    d.target.mini_selected
                        ? this.update_ani + this.remove_ani
                        : this.remove_ani
                )
                .attr(
                    "d",
                    d3
                        .linkHorizontal()
                        .x((d) => d.mini_y)
                        .y((d) => d.mini_x)
                )
                .style("opacity", (d) => (d.target.mini_selected ? 1 : 0));
        },
        expand_icon_update() {
            // this.expanded_icon_group
            //     .selectAll("path")
            //     .data([this.expand_tree])
            //     .attr("d", () => {
            //         if (this.expand_tree) {
            //             return Global.minus_path_d(0, 0, 10, 10, 2);
            //         } else {
            //             return Global.plus_path_d(0, 0, 10, 10, 2);
            //         }
            //     });
        },
        remove() {
            // this.mini_remove();
        },
        mini_remove() {},
    },
    watch: {
        f1_score_selected(){
            console.log("f1_score_selected");
            this.tree.all_descendants.forEach(d => {
                d.api = this.f1_score_selected ? d.f1_api : d.mm_api;
            })
            this.treecut();
            console.log("offset", this.offset);
            this.update_data();
            this.update_view();
        },
        tree() {
            console.log("tree update");
            this.treecut();
            console.log("offset", this.offset);
            this.update_data();
            this.update_view();
        },
        selected_flag(){
            console.log("selected flag update");
            this.update_data();
            this.update_view();
        },
        focus_node() {
            console.log("focus_node change", this.focus_node);
            this.treecut();
            console.log("offset", this.offset);
            this.update_data();
            this.update_view();
        },
        expand_tree() {
            console.log("expand tree change", this.expand_tree);
            // this.treecut(); // TODO:
            this.update_data();
            this.update_view();
        },
        expand_set_id(){
            console.log("watch expand set id");
            if (this.expand_set_id < 0){
                this.update_data();
                this.update_view();
            }
            else{
                this.fetch_grid_layout({});
            }
        },
        grid_data(){
            console.log("watch grid_data");
            this.update_data();
            this.update_view();
        }
    },
    async mounted() {
        console.log("detection mounted");
        window.detection = this;
        let container = d3.select(".main-content");
        let bbox = container.node().getBoundingClientRect();
        this.bbox_width = bbox.width;
        this.bbox_height = bbox.height;

        // text position
        this.text_height = this.bbox_height * 0.04;

        // node width
        this.max_text_width = 120; // fixed max_text_width

        // mini tree
        this.mini_tree_width = 35;
        this.mini_tree_height = 80;
        this.mini_tree_x = 120;
        this.mini_tree_y = 5;

        // detection result layout
        this.layout_width = this.bbox_width;
        this.layout_height = this.bbox_height - this.text_height;
        this.node_width = 20; // TODO
        this.layer_height = 40; // TODO

        // bar size
        this.bar_width = 6;
        this.bar_height = this.layer_height * 0.45;
        this.rounded_r = 1.5;

        // set
        this.set_num = 0;
        this.set_height = 0;
        this.image_height = 0;
        this.set_left = this.layer_height * 3 + 230;
        this.set_width = this.layout_width - this.set_left;
        this.set_margin = 6;
        this.image_margin = this.set_margin;

        // animation
        this.create_ani = Global.Animation;
        this.update_ani = Global.Animation;
        this.remove_ani = Global.Animation / 2;


        this.svg = container
            .append("svg")
            .attr("id", "main-svg")
            .attr("width", this.bbox_width)
            .attr("height", this.bbox_height)
            .style("padding-top", "5px");
        this.legend_create();
        this.expanded_icon_group = this.svg
            .append("g")
            .attr("id", "expanded-icon-group")
            .attr(
                "transform",
                "translate(" + 5 + ", " + this.text_height * 0.8 + ")"
            );
        this.tree_node_group = this.svg
            .append("g")
            .attr("id", "tree-node-group")
            .attr(
                "transform",
                "translate(" + 2 + ", " + this.layout_height / 2 + ")"
            );
        this.rest_node_group = this.svg
            .append("g")
            .attr("id", "rest-node-group")
            .attr(
                "transform",
                "translate(" + 2 + ", " + this.layout_height / 2 + ")"
            );
        this.mini_tree_node_group = this.svg
            .append("g")
            .attr("id", "mini-tree-node-group")
            .attr(
                "transform",
                "translate(" + this.mini_tree_x + ", " + this.mini_tree_y + ")"
            );
        this.mini_tree_link_group = this.svg
            .append("g")
            .attr("id", "mini-tree-link-group")
            .attr(
                "transform",
                "translate(" + this.mini_tree_x + ", " + this.mini_tree_y + ")"
            );
        this.mini_shadow_link_group = this.svg
            .append("g")
            .attr("id", "mini-shadow-link-group")
            .attr(
                "transform",
                "translate(" + this.mini_tree_x + ", " + this.mini_tree_y + ")"
            );
        this.set_group = this.svg
            .append("g")
            .attr("id", "set-group")
            .attr(
                "transform",
                "translate(" + 0 + ", " + this.text_height + ")"
            );
        this.grid_group = this.svg
            .append("g")
            .attr("id", "grid-group")
            .attr(
                "transform",
                "translate(" + 0 + ", " + this.text_height + ")"
            );
        this.label_group = this.svg
            .append("g")
            .attr("id", "label-group")
            .attr(
                "transform",
                "translate(" + 0 + ", " + this.text_height + ")"
            );
        this.nav_group = this.svg
            .append("g")
            .attr("id", "nav-group")
            .attr(
                "transform",
                "translate(" + 0 + ", " + 0 + ")"
            );

        this.set_link_group = this.svg
            .append("g")
            .attr("id", "set-link-group")
            .attr(
                "transform",
                "translate(" + 0 + ", " + this.text_height + ")"
            );

        this.tree_layout = new tree_layout(
            [this.node_width, this.layer_height],
            this.layout_height
        );

        this.mini_tree_layout = new mini_tree_layout([
            this.mini_tree_width,
            this.mini_tree_height,
        ]);

        this.treecut_class = new TreeCut(
            this.layer_height * 5,
            this.layout_height,
            this.layer_height
        );

        this.image_layout = new image_cluster_list_layout(this);
        this.connection_layout = new ConnectionLayout(this);
        // this.set_manager = new SetManager(this);

        this.text_tree_view = new TextTree(this);
        this.connection_view = new TextImageConnection(this);
        this.image_view = new ImageCards(this);
    },
};
</script>

<style>
/* .tree-node{
} */

.icon-bg-0 {
    cursor: pointer;
}

.node-name {
    pointer-events: none;
}

.rest-tree-node {
    cursor: pointer;
}

.tree-link {
    fill: none;
}

.set-link {
    fill: none;
}

.mini-tree-node {
    fill: #dfdfdf;
}

.bar-background {
    fill: white;
    stroke: rgb(127, 127, 127);
}

.bar-line {
    fill: rgb(127, 127, 127);
}

.bar-precision {
    fill: rgb(201, 130, 206);
}

.bar-recall {
    fill: rgb(79, 167, 255);
}

.mini-tree-link {
    stroke: #dfdfdf;
    fill: none;
}

/* .mini-shadow-link{
    stroke:
} */

.mini-highlight {
    stroke: #5f5f5f;
    fill: none;
}

.main-content {
    /* background: rgb(248, 249, 254); */
    background: rgb(255, 255, 255);
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: 100%;
}

.topname {
    display: flex;
    align-items: center;
    font-size: 20px;
    font-family: "Roboto", "Helvetica", "Arial", sans-serif;
    font-weight: 600;
    background: rgb(238, 238, 238);
    border-radius: 5px;
    padding-left: 10px;
    color: rgb(120, 120, 120);
    height: 22px;
}

#main-topname {
    display: flex;
    justify-content: space-between;
}

.matched-link{
    stroke: #D3D3E5;
}

.mismatched-link{
    stroke: #ED2939;
    stroke-dasharray: 5, 5;

}

.current-label-checkbox{
    cursor: pointer;
}
.prec-rec-checkbox{
    cursor: pointer;
}
.mismatch-checkbox{
    cursor: pointer;
}

.expand-path{
    pointer-events: none;
}

.waves-effect {
    position: relative;
    cursor: pointer;
    display: inline-block;
    overflow: hidden;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
    -webkit-tap-highlight-color: transparent;
    vertical-align: middle;
    z-index: 1;
    -webkit-transition: .3s ease-out;
    transition: .3s ease-out
}

.waves-effect .waves-ripple {
    position: absolute;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    margin-top: -10px;
    margin-left: -10px;
    opacity: 0;
    background: rgba(0,0,0,0.2);
    -webkit-transition: all 0.7s ease-out;
    transition: all 0.7s ease-out;
    -webkit-transition-property: opacity, -webkit-transform;
    transition-property: opacity, -webkit-transform;
    transition-property: transform, opacity;
    transition-property: transform, opacity, -webkit-transform;
    -webkit-transform: scale(0);
    transform: scale(0);
    pointer-events: none
}

.waves-effect.waves-light .waves-ripple {
    background-color: rgba(255,255,255,0.45)
}

.waves-effect.waves-red .waves-ripple {
    background-color: rgba(244,67,54,0.7)
}

.waves-effect.waves-yellow .waves-ripple {
    background-color: rgba(255,235,59,0.7)
}

.waves-effect.waves-orange .waves-ripple {
    background-color: rgba(255,152,0,0.7)
}

.waves-effect.waves-purple .waves-ripple {
    background-color: rgba(156,39,176,0.7)
}

.waves-effect.waves-green .waves-ripple {
    background-color: rgba(76,175,80,0.7)
}

.waves-effect.waves-teal .waves-ripple {
    background-color: rgba(0,150,136,0.7)
}

.waves-effect input[type="button"],.waves-effect input[type="reset"],.waves-effect input[type="submit"] {
    border: 0;
    font-style: normal;
    font-size: inherit;
    text-transform: inherit;
    background: none
}

.waves-effect img {
    position: relative;
    z-index: -1
}

.waves-notransition {
    -webkit-transition: none !important;
    transition: none !important
}

.waves-circle {
    -webkit-transform: translateZ(0);
    transform: translateZ(0);
    -webkit-mask-image: -webkit-radial-gradient(circle, white 100%, black 100%)
}

.waves-input-wrapper {
    border-radius: 0.2em;
    vertical-align: bottom
}

.waves-input-wrapper .waves-button-input {
    position: relative;
    top: 0;
    left: 0;
    z-index: 1
}

.waves-circle {
    text-align: center;
    width: 2.5em;
    height: 2.5em;
    line-height: 2.5em;
    border-radius: 50%;
    -webkit-mask-image: none
}

.waves-block {
    display: block
}

.waves-effect .waves-ripple {
    z-index: -1
}


.btn-floating {
    display: inline-block;
    color: #fff;
    position: relative;
    overflow: hidden;
    z-index: 1;
    width: 30px;
    height: 30px;
    line-height: 30px;
    padding: 0;
    background-color: #26a69a;
    border-radius: 50%;
    -webkit-transition: background-color .3s;
    transition: background-color .3s;
    cursor: pointer;
    vertical-align: middle
}


.btn-floating:hover {
    background-color: #26a69a
}

.btn-floating:before {
    border-radius: 0
}

.grey {
    background-color: #9e9e9e !important
}

.glyphicon {
  position: relative;
  top: 1px;
  display: inline-block;
  font-family: 'Glyphicons Halflings';
  font-style: normal;
  font-weight: normal;
  line-height: 1;

  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.glyphicon-zoom-in:before {
  content: "\e015";
}
</style>