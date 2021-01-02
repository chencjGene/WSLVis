<template>  
    <v-col cols="9" class="main-view fill-height">
        <v-col cols="12" class="main-content pa-0">
        </v-col>
    </v-col>
</template>

<script>
// import Vue from "vue"
import {mapActions, mapState, mapMutations} from "vuex"
import * as d3 from "d3"
import * as Global from '../plugins/global'
import {TreeCut, tree_layout} from "../plugins/treecut"
import {SetManager} from "../plugins/set_manager"
export default {
    name: "Detection",
    data: () =>({
        bbox_width: null,
        bbox_height: null,
        layout_width: null,
        layout_height: null,
        top_padding: null,
        nodes: null,
        links: null
    }),
    computed:{
        ...mapState([
           "tree", "set_list", "focus_node", "expand_tree" 
        ])
    },
    methods:{
        ...mapActions([
            "fetch_hypergraph"
        ]),
        ...mapMutations([
            "set_focus_node", "set_expand_tree"
        ]),
        treecut() {
            console.log("detection treecut");
            console.log("before treecut", this.tree);
            this.offset = this.treecut_class
                .treeCut(this.focus_node, this.tree, this.tree_layout.layout);
            this.offset = 0;
            this.tree.sort(function(a,b) {return a.siblings_id - b.siblings_id});
            console.log("after treecut", this.tree);
        },
        update_data() {
            console.log("detection update data");
            console.log(this.tree);
            const root = this.tree_layout.layout(this.tree);
            this.nodes = root.descendants().filter(d => d.name !== "root");
            this.max_text_width = this.nodes.map(d => 
                Global.getTextWidth(d.data.name, "16px Roboto, sans-serif"));
            console.log("max text width", this.max_text_width);
            this.max_text_width = Math.max(...this.max_text_width);
            this.leaf_nodes = this.nodes.filter(d => d.children.length == 0);
            console.log("leaf_nodes", this.leaf_nodes);
            this.set_manager.update_leaf_nodes(this.leaf_nodes);
            // this.set_manager.update_tree_root(2, this.layout_height / 2 - this.offset);
            let result = this.set_manager.get_sets();
            this.sets = result.sets;
            // this.set_links = result.set_links;
            this.set_links = []; // TODO: disable set links for debug
        },
        update_view() {
            console.log("detection update view");

            this.e_nodes = this.tree_node_group.selectAll(".tree-node")
            .data(this.nodes, d => d.id);
            this.e_sets = this.set_group.selectAll(".set")
            .data(this.sets); //TODO: id map
            this.e_set_links = this.set_link_group.selectAll(".set-link")
            .data(this.set_links); // TODO: id map

            // TODO: set remove ani when exit is none

            this.remove();
            this.update();
            this.create();
        },
        create(){
            console.log("Global", Global.GrayColor, Global.Animation);
            this.node_create();
            this.set_create();
            this.expand_icon_create();
        },
        node_create(){
            // node circle
            let node_groups = this.e_nodes.enter()
                .append("g")
                .attr("class", "tree-node")
                .attr("id", d => "id-" + d.id)
                .attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
            node_groups
                .on("mouseover", this.highlight)
                .on("mouseout", this.dehighlight)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", 1);
            node_groups
                .append("rect")
                .attr("class", "background")
                .attr("rx", this.layer_height / 6)
                .attr("ry", this.layer_height / 6)
                .attr("x", this.layer_height / 4)
                .attr("y", - this.layer_height * 0.8 / 2)
                .attr("height", this.layer_height * 0.8)
                .attr("width", () => {
                    // return Global.getTextWidth(d.data.name, "16px Roboto, sans-serif") + this.layer_height / 2; 
                    return this.max_text_width + 50;
                })
                .style("fill", "#EBEBF3")
                .style("fill-opacity", 0)
                .on("click", (ev, d) => {
                    console.log("click tree node", d.name);
                    this.set_focus_node(d);
                })
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("fill-opacity", 1);

            // // precision and recall
            // node_groups.append("g")
            //     .attr("class", "prob-bar")
            //     .selectAll("rect")
            //     .data(d => {
            //         let lens = [d.data.precision, d.data.recall];
            //         // let color = ["#FF9395", "#AAC6E6"];
            //         let color = ["gray", "gray"];
            //         return [
            //             {"len":lens[0], "color": color[0]},
            //             {"len":lens[1], "color": color[1]}
            //         ]
            //     })
            //     .enter()
            //     .append("rect")
            //     .attr("x", this.layer_height / 2)
            //     .attr("y", (_, i) => i * 3.5 + 8)
            //     .attr("height", 3)
            //     .attr("width", d => 80 * Math.pow(d.len, 0.8))
            //     .style("fill", d => d.color)
            //     .style("fill-opacity", 0)
            //     .transition()
            //     .duration(this.create_ani)
            //     .delay(this.remove_ani + this.update_ani)
            //     .style("fill-opacity", 1);

            node_groups
            .append("path")
            .attr("class", "icon")
            .attr("d", function(d){
                return Global.node_icon(0, 0, d.type);
            })
            .attr("fill", Global.GrayColor)
            .style("opacity", 0)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
            // node name
            node_groups.append("text")
            .text(d => {
                return d.name;
            })
            .attr("text-anchor", "start")
            .attr("x", this.layer_height / 2)
            .attr("dy", ".25em")
            .style("opacity", 0)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
            // node link
            node_groups.append("path")
            .attr("class", "node-link")
            .attr("d", d => {
                return  "M" + d.link_x + ", " + d.link_top + " L " 
                    + d.link_x + ", " + d.link_bottom;
            })
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 0.5)
            .style("opacity", 0)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
        },
        set_create(){
            // set
            let set_groups = this.e_sets.enter()
            .append("g")
            .attr("class", "set")
            .attr("transform", d => "translate(" + d.x + 
                ", " + d.y + ")");

            set_groups.append("rect")
            .attr("class", "background")
            .style("fill", "white")
            .style("stroke", "#f0f0f0")
            .style("stroke-width", 1)
            .style("opacity", 0)
            .attr("width", d => d.width)
            .attr("height", d => d.height)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);

            // set links
            this.e_set_links.enter()
            .append("path")
            .attr("class", "set-link")
            // .attr("d", Global.set_line)
            .attr("d",  d3.linkHorizontal().x(d=>d.x).y(d=>d.y))
            .style("opacity", 0)
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 0.5)
            .style("stroke-dasharray", "5, 5")
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
        },
        title_create(){
            this.svg.append("text")
                .attr("class", "topname")
                .attr("x", this.layer_height / 2)
                .attr("y", this.text_height / 2 + 1)
                .text("Category");
            this.svg.append("text")
                .attr("class", "topname")
                .attr("x", this.set_left * 1.05)
                .attr("y", this.text_height / 2 + 1)
                .text("Detection");
        },
        expand_icon_create(){
            this.expanded_icon_group
                .on("click", () => {
                    console.log("click expanded icon", this.expand_tree);
                    this.set_expand_tree(!this.expand_tree);
                })
            this.expanded_icon_group
                .selectAll("rect")
                .data([this.expand_tree])
                .enter()
                .append("rect")
                .attr("width", 10)
                .attr("height", 10)
                .style("rx", 3)
                .style("ry", 3)
                .style("fill", "white")
                .style("stroke", "gray")
                .style("stroke-width", 1);
            this.expanded_icon_group
                .selectAll("path")
                .data([this.expand_tree])
                .enter()
                .append("path")
                .style("stroke", "none")
                .style("fill", "gray")
                .attr("d", () => {
                    if (this.expand_tree){
                        return Global.minus_path_d(0, 0, 10, 10, 2);
                    }
                    else{
                        return Global.plus_path_d(0, 0, 10, 10, 2);
                    }
                });
        },
        update(){
            this.node_update();
            this.set_update();
            this.expand_icon_update();
        },
        node_update(){

            this.tree_node_group
            .attr("transform", "translate(" + this.layer_height / 2 + ", " 
                + (this.text_height + this.layer_height / 2) + ")");
            this.e_nodes
            .transition()
            .duration(this.update_ani)
            .delay(this.remove_ani)
            .attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
            this.e_nodes.select("rect.background")
                .transition()
                .duration(this.update_ani)
                .attr("x", this.layer_height / 4)
                .attr("y", - this.layer_height * 0.8 / 2)
                .attr("height", this.layer_height * 0.8)
                .attr("width", () => {
                    // return Global.getTextWidth(d.data.name, "16px Roboto, sans-serif") + this.layer_height / 2; 
                    return this.max_text_width + 50;
                });
            
            this.e_nodes.select("path.icon")
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("d", function(d){
                    return Global.node_icon(0, 0, d.type);
                });
            this.e_nodes.select("text")
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .text(d => d.name)
                .style("opacity", 1);
            this.e_nodes.select("path.node-link")
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("d", d => {
                    return  "M" + d.link_x + ", " + d.link_top + " L " 
                        + d.link_x + ", " + d.link_bottom;
                });
        },
        set_update(){

        },
        expand_icon_update(){       
            this.expanded_icon_group
                .selectAll("path")
                .data([this.expand_tree])
                .attr("d", () => {
                    if (this.expand_tree){
                        return Global.minus_path_d(0, 0, 10, 10, 2);
                    }
                    else{
                        return Global.plus_path_d(0, 0, 10, 10, 2);
                    }
                });
        },
        remove(){
            this.e_nodes.exit()
                .remove();
            this.e_sets.exit()
                .remove();
            this.e_set_links.exit()
                .remove()
        },
        node_remove(){

        },
        highlight(ev, d){
            // console.log("highlight in tree");
            this.tree_node_group.select("#id-" + d.id)
                .select("rect.background")
                .style("fill", "#E0E0EC");
        },
        dehighlight(){
            // console.log("dehighlight in tree");
            this.svg.selectAll("g.tree-node")
                .select("rect.background")
                .style("fill", "#EBEBF3");
        }
    },
    watch:{
        tree(){
            console.log("tree update");
            this.treecut();
            console.log("offset", this.offset);
            this.update_data();
            this.update_view();
        },
        focus_node(){
            console.log("focus_node change", this.focus_node);
            this.treecut();
            console.log("offset", this.offset);
            this.update_data();
            this.update_view();
        },
        expand_tree(){
            console.log("expand tree change", this.expand_tree);
            // this.treecut(); // TODO:
            this.update_data();
            this.update_view();
        },
    },
    async mounted(){
        console.log("detection mounted");
        window.detection = this;
        let container = d3.select(".main-content");
        let bbox = container.node().getBoundingClientRect();
        this.bbox_width = bbox.width;
        this.bbox_height = bbox.height;
        
        // text position
        this.text_height = this.bbox_height * 0.05; 

        // detection result layout 
        this.layout_width = this.bbox_width;
        this.layout_height = this.bbox_height - this.text_height;
        this.node_width = 20; // TODO
        this.layer_height = 40; // TODO
        this.set_height = 112;
        this.set_left = this.layer_height * 3 + 200;
        this.set_width = this.layout_width - this.set_left;
        this.set_margin = 6;
        this.create_ani = Global.Animation;
        this.update_ani = Global.Animation;
        this.remove_ani = 0;
        this.svg = container.append("svg")
            .attr("id", "main-svg")
            .attr("width", this.bbox_width)
            .attr("height", this.bbox_height)
            .style("padding-top", "5px");
        this.title_create();
        this.expanded_icon_group = this.svg.append("g")
            .attr("id", "expanded-icon-group")
            .attr("transform", "translate(" + (1) + ", " + (this.text_height) + ")");
        this.tree_node_group = this.svg.append("g")
            .attr("id", "tree-node-group")
            .attr("transform", "translate(" + 2 + ", " + (this.layout_height / 2) + ")");
        this.set_group = this.svg.append("g")
            .attr("id", "set-group")
            .attr("transform", "translate(" + 0 + ", " + (this.text_height) + ")");
        this.set_link_group = this.svg.append("g")
            .attr("id", "set-link-group")
            .attr("transform", "translate(" + 0 + ", " + (this.text_height) + ")");

        this.tree_layout = new tree_layout([this.node_width, this.layer_height]);

        this.treecut_class = new TreeCut(this.layer_height * 3, this.layout_height);

        this.set_manager = new SetManager();
        this.set_manager.update_layout({
            "layout_width": this.layout_width,
            "layout_height": this.layout_height,
            "set_left": this.set_left,
            "set_width": this.set_width,
            "set_margin": this.set_margin,
            "set_height": this.set_height
        })
    }
}
</script>

<style>
.tree-node{
    cursor: pointer;
}

.tree-link{
    fill: none;
}

.set-link{
    fill: none;
}

.main-content {
  background: rgb(248, 249, 254);
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
</style>