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
            <div id="grid-control" style="position: absolute; padding-left: 600px; padding-top: 10px; display: none;" >
                <div id="cropping" class="waves-effect waves-light btn-floating grey" title="Zoom in">
                    <svg class="icon" width="24px" height="24px" transform="translate(2.6, 2.6)" viewBox="0 0 1024 1024">
                        <path fill="white" d="M136 384h56c4.4 0 8-3.6 8-8V200h176c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H196c-37.6 0-68 30.4-68 68v180c0 4.4 3.6 8 8 8zM648 200h176v176c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8V196c0-37.6-30.4-68-68-68H648c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8zM376 824H200V648c0-4.4-3.6-8-8-8h-56c-4.4 0-8 3.6-8 8v180c0 37.6 30.4 68 68 68h180c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8zM888 640h-56c-4.4 0-8 3.6-8 8v176H648c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h180c37.6 0 68-30.4 68-68V648c0-4.4-3.6-8-8-8zM904 476H120c-4.4 0-8 3.6-8 8v56c0 4.4 3.6 8 8 8h784c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8z" />
                    </svg>
                </div>
                <div id="selecting" style="margin-left: 3px" class="waves-effect waves-light btn-floating grey" title="Select">
                    <svg class="icon" width="24px" height="24px" transform="translate(2.6, 2.6)"  viewBox="0 0 1024 1024">
                        <path fill="white" d="M880 112H144c-17.7 0-32 14.3-32 32v736c0 17.7 14.3 32 32 32h360c4.4 0 8-3.6 8-8v-56c0-4.4-3.6-8-8-8H184V184h656v320c0 4.4 3.6 8 8 8h56c4.4 0 8-3.6 8-8V144c0-17.7-14.3-32-32-32zM653.3 599.4l52.2-52.2c4.7-4.7 1.9-12.8-4.7-13.6l-179.4-21c-5.1-0.6-9.5 3.7-8.9 8.9l21 179.4c0.8 6.6 8.9 9.4 13.6 4.7l52.4-52.4 256.2 256.2c3.1 3.1 8.2 3.1 11.3 0l42.4-42.4c3.1-3.1 3.1-8.2 0-11.3L653.3 599.4z" />
                    </svg>
                </div>
                <div id="home" style="margin-left: 3px" class="waves-effect waves-light btn-floating grey" title="Home">
                    <svg class="icon" width="24px" height="24px" transform="translate(2.6, 2.6)"  viewBox="0 0 1024 1024">
                        <path fill="white" d="M1057.756543 566.281052a44.505707 44.505707 0 0 1-62.953323 0L535.326296 108.094795 150.99726 491.311188h27.927332a89.011415 89.011415 0 0 1 89.011414 89.011415v47.287314l0.244782 268.057876c3.004135 28.817446 13.173689 36.828473 44.950764 39.076011 39.276287-2.892871 43.571088-14.976171 43.971639-64.17723l-0.15577-113.06675a89.011415 89.011415 0 0 1 89.011415-88.165806h44.505707v-1.09039l89.011415-0.133517v1.223907h44.505708a89.011415 89.011415 0 0 1 89.011414 89.011415v47.287314h0.15577v56.010432l0.133517-14.953917c0 69.718191-0.445057 84.560844 44.105156 87.921025 37.451553-2.981882 43.660099-14.442102 44.639225-57.85742l-0.400551 58.346982h0.667585v-73.92398c0 5.629972 0 10.770381-0.178023 15.576998l0.178023-26.102597-0.289287-272.352677a44.505707 44.505707 0 0 1 89.011415 0l0.31154 309.314667h-0.31154V934.988585a89.011415 89.011415 0 0 1-89.011415 89.011415h-89.011415a88.833392 88.833392 0 0 1-88.655369-85.450958L624.159688 823.724317l-0.378298-17.668766c0.15577 2.358802 0.267034 5.029145 0.378298 7.610476L623.981666 756.965756h-24.47814l23.120715 0.15577 1.068137 48.956278c-2.737101-39.165023-13.551988-47.287314-53.896411-48.956278h-73.634693c-37.362541 1.891493-47.376326 10.169554-50.002162 44.928511l0.979125-44.8395h-1.179401v46.441706c0-0.556321 0-1.068137 0.133517-1.602206l-0.133517 5.741236 0.133517 79.798734h-0.133517V934.988585a89.011415 89.011415 0 0 1-89.011415 89.011415h-89.011415a88.833392 88.833392 0 0 1-88.633116-85.183924l-0.378298-359.761886h-18.848168 17.535249l0.400552 59.504131c-1.045884-47.665613-7.855257-57.523627-50.714254-59.548636l-80.288296 0.200275a43.59334 43.59334 0 0 1-11.126427-0.845608l-1.045884-0.200276A40.055137 40.055137 0 0 1 0.901762 544.228474c0-0.289287-0.111264-0.600827-0.15577-0.890114a43.103778 43.103778 0 0 1-0.289287-14.241826 48.956278 48.956278 0 0 1 3.315675-12.305828 44.260926 44.260926 0 0 1 7.944269-11.949783c0.244781-0.244781 0.289287-0.556321 0.534068-0.801103L500.411569 17.258646a47.376326 47.376326 0 0 1 2.781607-4.20579 44.505707 44.505707 0 0 1 62.953323 0l0.645333 0.645333 490.897952 489.562782a44.505707 44.505707 0 0 1 0.066759 63.020081zM713.349126 935.300125h21.140211l-21.140211-0.133517v0.178023z m-445.057074 0h21.117958l-21.117958-0.133517v0.178023zM178.034477 638.714091c0.178023 9.145923 0.200276 19.560258 0.200276 31.710317z" />
                    </svg>
                </div>
            </div>
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
                    this.tree.all_descendants.forEach(d => d.children = []);
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
            if (!this.use_treecut){
                this.tree_layout.update_layout_by_num(this.tree.descendants().length - 1);
            }
            else{
                this.tree_layout.reset_layout();
            }
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
            /**  svg-dropdown.js - svg dropdown library  */
            function svgDropDown(options) {
                if (typeof options !== 'object' || options === null || !options.container) {
                  console.error(new Error("Container not provided"));
                  return;
                }
                const defaultOptions = {
                  width: 200,
                  members: [],
                  fontSize: 12,
                  color: "#333",
                  fontFamily: "Calibri,Candara,Segoe,Segoe UI,Optima,Arial,sans-serif",
                  x: 0,
                  y: 0,
                  changeHandler: function() {}
                };

                options = { ...defaultOptions,
                  ...options
                };

                options.optionHeight = options.fontSize * 2;
                options.height = options.fontSize + 8;
                options.padding = 5;
                options.hoverColor = "#0c56f5";
                options.hoverTextColor = "#fff";
                options.bgColor = "#fff";
                options.width = options.width - 2;

                const g = options.container
                  .append("svg")
                  .attr("x", options.x)
                  .attr("y", options.y)
                  .attr("shape-rendering", "crispEdges")
                  .append("g")
                  .attr("transform", "translate(1,1)")
                  .attr("font-family", options.fontFamily);

                let selectedOption =
                  options.members.length === 0 ? {
                    label: "",
                    value: ""
                  } :
                  options.members[options.initMember];

                /** Rendering Select Field */
                const selectField = g.append("g");

                // background
                selectField
                  .append("rect")
                  .attr("width", options.width)
                  .attr("height", options.height)
                  .attr("class", "option select-field")
                  .attr("fill", options.bgColor)
                  .style("stroke", "#a0a0a0")
                  .style("stroke-width", "1");

                // text
                const activeText = selectField
                  .append("text")
                  .text(selectedOption.label)
                  .attr("x", options.padding)
                  .attr("y", options.height / 2 + options.fontSize / 3)
                  .attr("font-size", options.fontSize)
                  .attr("fill", options.color);

                // arrow symbol at the end of the select box
                selectField
                  .append("text")
                  .text("▼")
                  .attr("x", options.width - options.fontSize - options.padding)
                  .attr("y", options.height / 2 + (options.fontSize - 2) / 3)
                  .attr("font-size", options.fontSize - 2)
                  .attr("fill", options.color);

                // transparent surface to capture actions
                selectField
                  .append("rect")
                  .attr("width", options.width)
                  .attr("height", options.height)
                  .style("fill", "transparent")
                  .on("click", handleSelectClick);

                /** rendering options */
                const optionGroup = g
                  .append("g")
                  .attr("transform", `translate(0, ${options.height})`)
                  .attr("opacity", 0); //.attr("display", "none"); Issue in IE/Firefox: Unable to calculate textLength when display is none.

                // Rendering options group
                const optionEnter = optionGroup
                  .selectAll("g")
                  .data(options.members)
                  .enter()
                  .append("g")
                  .on("click", handleOptionClick);

                // Rendering background
                optionEnter
                  .append("rect")
                  .attr("width", options.width)
                  .attr("height", options.optionHeight)
                  .attr("y", function(d, i) {
                    return i * options.optionHeight;
                  })
                  .attr("class", "option")
                  .style("stroke", options.hoverColor)
                  .style("stroke-dasharray", (d, i) => {
                    let stroke = [
                      0,
                      options.width,
                      options.optionHeight,
                      options.width,
                      options.optionHeight
                    ];
                    if (i === 0) {
                      stroke = [
                        options.width + options.optionHeight,
                        options.width,
                        options.optionHeight
                      ];
                    } else if (i === options.members.length - 1) {
                      stroke = [0, options.width, options.optionHeight * 2 + options.width];
                    }
                    return stroke.join(" ");
                  })
                  .style("stroke-width", 1)
                  .style("fill", options.bgColor);

                // Rendering option text
                optionEnter
                  .append("text")
                  .attr("x", options.padding)
                  .attr("y", function(d, i) {
                    return (
                      i * options.optionHeight +
                      options.optionHeight / 2 +
                      options.fontSize / 3
                    );
                  })
                  .text(function(d) {
                    return d.label;
                  })
                  .attr("font-size", options.fontSize)
                  .attr("fill", options.color)
                  .each(wrap);

                // Rendering option surface to take care of events
                optionEnter
                  .append("rect")
                  .attr("width", options.width)
                  .attr("height", options.optionHeight)
                  .attr("y", function(d, i) {
                    return i * options.optionHeight;
                  })
                  .style("fill", "transparent")
                  .on("mouseover", handleMouseOver)
                  .on("mouseout", handleMouseOut);

                //once the textLength gets calculated, change opacity to 1 and display to none
                optionGroup.attr("display", "none").attr("opacity", 1);

                d3.select("body").on("click", function() {
                  optionGroup.attr("display", "none");
                });

                // Utility Methods
                function handleMouseOver(event) {
                  d3.select(event.target.parentNode)
                    .select(".option")
                    .style("fill", options.hoverColor);

                  d3.select(event.target.parentNode)
                    .select("text")
                    .style("fill", options.hoverTextColor);
                }

                function handleMouseOut(event) {
                  d3.select(event.target.parentNode)
                    .select(".option")
                    .style("fill", options.bgColor);

                  d3.select(event.target.parentNode)
                    .select("text")
                    .style("fill", options.color);
                }

                function handleOptionClick(event, d) {
                  event.stopPropagation();
                  selectedOption = d;
                  activeText.text(selectedOption.label).each(wrap);
                  typeof options.changeHandler === 'function' && options.changeHandler.call(this, d);
                  optionGroup.attr("display", "none");
                }

                function handleSelectClick(event) {
                    console.log(event);
                  event.stopPropagation();
                  const visibility = optionGroup.attr("display") === "block" ? "none" : "block";
                  optionGroup.attr("display", visibility);
                }

                // wraps words
                function wrap() {
                  const width = options.width;
                  const padding = options.padding;
                  const self = d3.select(this);
                  let textLength = self.node().getComputedTextLength();
                  let text = self.text();
                  const textArr = text.split(/\s+/);
                  let lastWord = "";
                  while (textLength > width - 2 * padding && text.length > 0) {
                    lastWord = textArr.pop();
                    text = textArr.join(" ");
                    self.text(text);
                    textLength = self.node().getComputedTextLength();
                  }
                  self.text(text + " " + lastWord);

                  // providing ellipsis to last word in the text
                  if (lastWord) {
                    textLength = self.node().getComputedTextLength();
                    text = self.text();
                    while (textLength > width - 2 * padding && text.length > 0) {
                      text = text.slice(0, -1);
                      self.text(text + "...");
                      textLength = self.node().getComputedTextLength();
                    }
                  }
                }
              }

            let that = this;
            let top_y = 4;
            let drop_down_width = 100;
            let start_x = 15;

            // treecut: dropdown-list
             let treecut_g = that.svg
                .append("g")
                .attr("class", "current-label-checkbox")
                .attr("transform", "translate("+
                    (start_x)+","+
                    (top_y)+")" + "scale(" + 1+"," + 1+")");
             treecut_g.append("text")
                .attr("text-anchor", "start")
                .attr("x", 14 + 2)
                .attr("y", 20)
                .attr("font-size", "18px")
                .text("Treecut");
             let members = [{
                  label: "None",
                  value: 1
                },
                {
                  label: "F1 score",
                  value: 2
                },
                {
                  label: "Mismatch",
                  value: 3
                }
             ];

             let config = {
                width: drop_down_width,
                container: treecut_g,
                members: members,
                fontSize: 18,
                color: "#333",
                fontFamily: "calibri",
                x: 80,
                y: 0,
                 initMember:2,
                changeHandler: function(option) {
                    if(option.label==="None") {
                        console.log("click tree cut", that.use_treecut);
                        that.set_use_treecut(false);
                        // if (that.use_treecut){
                        //     that.set_use_treecut(false);
                        //     // d3.select(this).select("rect")
                        //     //     .attr("fill", "white");
                        //     // d3.selectAll(".prec-rec-checkbox")
                        //     //     .select("rect")
                        //     //     .attr("fill", "white");
                        //     // d3.selectAll(".mismatch-checkbox")
                        //     //     .select("rect")
                        //     //     .attr("fill", "white");
                        // }
                        // else{
                        //     that.set_use_treecut(true);
                        //     // d3.select(this).select("rect")
                        //     //     .attr("fill", Global.GrayColor);
                        //     // d3.selectAll(".prec-rec-checkbox")
                        //     //     .select("rect")
                        //     //     .attr("fill", that.f1_score_selected ? Global.GrayColor : "white")
                        //     // d3.selectAll(".mismatch-checkbox")
                        //     //     .select("rect")
                        //     //     .attr("fill", that.f1_score_selected ? "white" : Global.GrayColor)
                        // }
                    } else if(option.label==="F1 score") {
                        console.log("click prec-rec-checkbox", that.f1_score_selected);
                        if (that.use_treecut && !that.f1_score_selected){
                            that.set_f1_score_selected(true);
                            d3.select(this).select("rect")
                                .attr("fill", Global.GrayColor);
                            d3.selectAll(".mismatch-checkbox")
                                .select("rect")
                                .attr("fill", "white");
                        }
                    } else if(option.label==="Mismatch") {
                        console.log("click prec-rec-checkbox", that.f1_score_selected);
                        if (that.use_treecut && that.f1_score_selected){
                            that.set_f1_score_selected(false);
                            d3.select(this).select("rect")
                                .attr("fill", Global.GrayColor);
                            d3.selectAll(".prec-rec-checkbox")
                                .select("rect")
                                .attr("fill", "white");
                        }
                    } else {
                        console.log("ERROR: no option named", option.label)
                    }
                }
             };
             svgDropDown(config);

             // co-occurrence: dropdown-list
            let cooccurence_x = start_x+drop_down_width+80+30;
            let cooccurrence_dropdown_width = 150;
            let cooccurence_g = that.svg
                .append("g")
                .attr("class", "current-label-checkbox")
                .attr("transform", "translate("+
                    (cooccurence_x)+","+
                    (top_y)+")" + "scale(" + 1+"," + 1+")");
             cooccurence_g.append("text")
                .attr("text-anchor", "start")
                .attr("x", 14 + 2)
                .attr("y", 20)
                .attr("font-size", "18px")
                .text("Co-occurrence");
             let cooccurrenceMembers = [{
                  label: "Extracted labels",
                  value: 5
                },
                {
                  label: "Detected objects",
                  value: 6
                }
             ];

             let cooccurrenceConfig = {
                width: cooccurrence_dropdown_width,
                container: cooccurence_g,
                members: cooccurrenceMembers,
                fontSize: 18,
                color: "#333",
                fontFamily: "calibri",
                x: 140,
                y: 0,
                initMember:0,
                changeHandler: function(option) {
                    if(option.label==="Extracted labels") {
                        console.log("select option: Extracted labels")
                    } else if(option.label==="Detected objects") {
                        console.log("select option: Detected objects")
                    }
                }
             };
             svgDropDown(cooccurrenceConfig);

            // precision & recall legend
            let precision_color = "rgb(201, 130, 206)";
            let recall_color = "rgb(79, 167, 255)";
            let rect_size = 6;
            let precision_recall_legend_startx = cooccurence_x+cooccurrence_dropdown_width+140+50;
            let pc_group = that.svg
                .append("g")
                .attr("class", "precision-recall-legend")
                .attr("transform", "translate("+
                    (precision_recall_legend_startx)+","+
                    (top_y)+")" + "scale(" + 1+"," + 1+")");
            pc_group.append("rect")
                .attr("x", 0)
                .attr("y", rect_size)
                // .attr("y", rect_size+10)
                .attr("rx", 1.5)
                .attr("ry", 1.5)
                .attr("width", rect_size)
                .attr("height", rect_size)
                .attr("stroke-width", 1)
                .attr("stroke", precision_color)
                .attr("fill", precision_color);
            pc_group.append("rect")
                .attr("x", 0)
                .attr("y", 0)
                // .attr("y", 10)
                .attr("rx", 1.5)
                .attr("ry", 1.5)
                .attr("width", rect_size)
                .attr("height", rect_size*2)
                .attr("stroke-width", 1)
                .attr("stroke", precision_color)
                .attr("fill", "none");

            pc_group.append("rect")
                // .attr("x", rect_size+93)
                .attr("x", 0)
                .attr("y", rect_size+20)
                // .attr("y", rect_size+10)
                .attr("rx", 1.5)
                .attr("ry", 1.5)
                .attr("width", rect_size)
                .attr("height", rect_size)
                .attr("stroke-width", 1)
                .attr("stroke", recall_color)
                .attr("fill", recall_color);
            pc_group.append("rect")
                // .attr("x", rect_size+93)
                .attr("x", 0)
                .attr("y", 20)
                // .attr("y", 10)
                .attr("rx", 1.5)
                .attr("ry", 1.5)
                .attr("width", rect_size)
                .attr("height", rect_size*2)
                .attr("stroke-width", 1)
                .attr("stroke", recall_color)
                .attr("fill", "none");

            pc_group.append("text")
                .attr("text-anchor", "start")
                .attr("x", rect_size+5)
                .attr("y", 0)
                // .attr("y", 22)
                // .attr("font-size", "18px")
                .style("dominant-baseline", "hanging")
                .text("Precision");

            pc_group.append("text")
                .attr("text-anchor", "start")
                .attr("x", rect_size+5)
                // .attr("x", rect_size*2+98)
                .attr("y", 20)
                // .attr("y", 22)
                // .attr("font-size", "18px")
                .style("dominant-baseline", "hanging")
                .text("Recall");

            // match & mismatch line legend
            let match_color = "#D3D3E5";
            let mistach_color = "#ED2939";
            let line_stroke = 1;
            let line_length = 30;
            let match_mismatch_legend_startx = precision_recall_legend_startx+60+50;
            let match_group = that.svg
                .append("g")
                .attr("id", "match-mismatch-legend-group")
                .attr("transform", "translate("+
                    (match_mismatch_legend_startx)+","+
                    (top_y)+")" + "scale(" + 1+"," + 1+")");
            match_group  
                .selectAll(".match-mismatch-legend")
                .data(["Mismatched cluster pair", "Matched cluster pair"])
                .enter()
                .append("g")
                .attr("class", "match-mismatch-legend")
                .each(function(d, i) {
                    let group = d3.select(this);
                    group.append("line").attr("x1", 0).attr("y1", 20 * i + 7.5).attr("x2", line_length).attr("y2", 20 * i + 7.5).attr("stroke-dasharray", i === 0 ? "5,5" : "5,0").style("stroke-width", line_stroke).style("stroke", i === 0 ? mistach_color : match_color);
                    group.append("text").attr("x", 40).attr("y", 20 * i).text(d).style("dominant-baseline", "hanging");
                });
            // match_group.append("line")
            //     .attr("x1", 0)
            //     .attr("y1", 15)
            //     .attr("x2", line_length)
            //     .attr("y2", 15)
            //     .attr("stroke-width", line_stroke)
            //     .attr("stroke", match_color);

            // match_group.append("line")
            //     .attr("x1", 220)
            //     .attr("y1", 15)
            //     .attr("x2", line_length+220)
            //     .attr("y2", 15)
            //     .attr("stroke-dasharray", "5,5")
            //     .attr("stroke-width", line_stroke)
            //     .attr("stroke", mistach_color);

            // match_group.append("text")
            //     .attr("text-anchor", "start")
            //     .attr("x", 3+line_length)
            //     .attr("y", 22)
            //     .attr("font-size", "18px")
            //     .text("Matched cluster pair");

            // match_group.append("text")
            //     .attr("text-anchor", "start")
            //     .attr("x", line_length+220)
            //     .attr("y", 22)
            //     .attr("font-size", "18px")
            //     .text("Mismatched cluster pair");

            // 4. Grid_layout legend and buttons
            let grid_legend_startx = match_mismatch_legend_startx + 200 + 50;
            let grid_legend_group = this.svg
                .append("g")
                .attr("id", "grid-legend-group")
                .attr("transform", "translate("+
                    (grid_legend_startx)+","+
                    (top_y)+")" + "scale(" + 1+"," + 1+")")
                .style("visibility", "hidden");
            grid_legend_group  
                .selectAll(".grid-legend")
                .data(["Mismatched Samples", "Matched Samples"])
                .enter()
                .append("g")
                .attr("class", "grid-legend")
                .each(function(d, i) {
                    let group = d3.select(this);
                    group.append("rect").attr("x", 0).attr("y", 20 * i).attr("width", 15).attr("height", 15).style("fill", i === 0 ? "rgb(255, 169, 83)" : Global.GrayColor);
                    group.append("text").attr("x", 20).attr("y", 20 * i).text(d).style("dominant-baseline", "hanging");
                });
            d3.select("#grid-control")
                .style("padding-left", (grid_legend_startx + 200) + "px");
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
        use_treecut(){
            console.log("use_treecut");
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
        this.nav_group.style("visibility", "hidden");
        this.set_link_group = this.svg
            .append("g")
            .attr("id", "set-link-group")
            .attr(
                "transform",
                "translate(" + 0 + ", " + this.text_height + ")"
            );
        this.legend_create();
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
    justify-content: space-between;
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