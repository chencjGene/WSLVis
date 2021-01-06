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
        </v-col>
    </v-col>
</template>

<script>
// import Vue from "vue"
import {mapActions, mapState, mapMutations} from "vuex"
import * as d3 from "d3"
import * as Global from '../plugins/global'
import {mini_tree_layout, TreeCut, tree_layout} from "../plugins/treecut"
import {SetManager} from "../plugins/set_manager"
import InfoTooltip from "../components/infotooltip";
export default {
    name: "Detection",
    components:{
        InfoTooltip: InfoTooltip
    },
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
           "tree", "set_list", "focus_node", "expand_tree", "tooltip"
        ])
    },
    methods:{
        ...mapActions([
            "fetch_hypergraph"
        ]),
        ...mapMutations([
            "set_focus_node", "set_expand_tree", "showTooltip", "hideTooltip"
        ]),
        treecut() {
            console.log("detection treecut");
            console.log("before treecut", this.tree);
            this.offset = this.treecut_class
                .treeCut(this.focus_node, this.tree, this.tree_layout.layout_with_nodes);
            this.offset = 0;
            this.tree.sort(function(a,b) {return a.siblings_id - b.siblings_id});
            console.log("after treecut", this.tree);
        },
        update_data() {
            console.log("detection update data");
            console.log(this.tree);
            // tree layout
            this.nodes = this.tree_layout.layout_with_rest_node(this.tree, this.expand_tree);
            this.rest_nodes = this.nodes.filter(d => d.is_rest_node);
            this.nodes = this.nodes.filter(d => !d.is_rest_node);
            // minitree layout
            let mat = this.mini_tree_layout.layout(this.tree);
            this.mini_nodes = mat.nodes;
            this.mini_links = mat.links;
            // set layout
            // this.max_text_width = this.nodes.map(d =>
            //     Global.getTextWidth(d.data.name, "16px Roboto, sans-serif"));
            // console.log("max text width", this.max_text_width);
            // this.max_text_width = Math.max(...this.max_text_width) + 10;
            this.max_text_width = 120;
            this.leaf_nodes = this.nodes.filter(d => d.children.length === 0);
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
            this.e_rest_nodes = this.rest_node_group.selectAll(".rest-tree-node")
                .data(this.rest_nodes, d => d.id);
            this.e_mini_nodes = this.mini_tree_node_group.selectAll(".mini-tree-node")
                .data(this.mini_nodes, d => d.id);
            this.e_mini_links = this.mini_tree_link_group.selectAll(".mini-tree-link")
                .data(this.mini_links);
            this.e_shadow_links = this.mini_shadow_link_group.selectAll(".mini-highlight")
                .data(this.mini_links);
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
            this.mini_create();
        },
        node_create(){
            // node circle
            let node_groups = this.e_nodes.enter()
                .append("g")
                .attr("class", "tree-node")
                .attr("id", d => "id-" + d.id)
                .attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
            node_groups
                .on("mouseover", (ev, d) => {
                    // let left = d.x + this.layer_height / 4 + this.max_text_width + 
                    //     (this.expand_tree ? this.layer_height / 2 : 0) + 20;
                    // let top = d.y + this.text_height + this.layer_height / 2;
                    // let width = Global.getTextWidth(d.full_name, "18px Roboto, sans-serif") + 20;
                    // console.log("mouseover", left, top);
                    // this.showTooltip({top, left, width, content: d.full_name});
                    this.highlight(ev, d);
                })
                .on("mouseout", () => {
                    // this.hideTooltip();
                    this.dehighlight();
                })
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", 1);
            node_groups.append("title")
                .style("font-size", "18px")
                .text(d => d.full_name);
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
                    return this.max_text_width;
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

            
            // precision and recall
            let bars = node_groups.append("g")
                .attr("class", "node-bars")
                .attr("transform", () => "translate(" + (this.max_text_width - 15) + 
                    ", " + (- (this.bar_height - this.rounded_r) / 2) + ")");
            bars.append("rect")
                .attr("class", "bar-background")
                .attr("rx", this.rounded_r)
                .attr("ry", this.rounded_r)
                .attr("y",  - this.rounded_r)
                .attr("width", this.bar_width * 2)
                .attr("height", this.bar_height + this.rounded_r);
            bars.append("path")
                .attr("class", "bar-precision")
                .attr("d", d => Global.half_rounded_rect(0, (1 - d.data.precision) * this.bar_height,
                    this.bar_width, d.data.precision * this.bar_height, this.rounded_r, 0));
            bars.append("path")
                .attr("class", "bar-recall")
                .attr("d", d => Global.half_rounded_rect(this.bar_width, (1 - d.data.recall) * this.bar_height, 
                    this.bar_width, d.data.recall * this.bar_height, 0, this.rounded_r));
            bars.append("rect")
                .attr("class", "bar-line")
                .attr("x", this.bar_width - 0.5 / 2)
                .attr("y", - this.rounded_r)
                .attr("width", 0.5)
                .attr("height", this.bar_height + this.rounded_r);
            bars.style("opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", 1);

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
            .style("opacity", () => this.expand_tree ? 1 : 0);
            // node name
            node_groups.append("text")
            .text(d => {
                return d.name;
            })
            .attr("text-anchor", "start")
            .attr("x", this.layer_height / 2)
            .attr("font-size", "18px")
            .attr("dy", ".3em")
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
        mini_create(){
            this.e_mini_nodes.enter()
                .append("circle")
                .attr("class", "mini-tree-node")
                .attr("id", d => "mini-id-" + d.id)
                .attr("r", 0.5)
                .attr("cx", d => d.mini_y)
                .attr("cy", d => d.mini_x)
                .style("fill-opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("fill-opacity", 1);
            this.e_mini_links.enter()
                .append("path")
                .attr("class", "mini-tree-link")
                .attr("d", d3.linkHorizontal().x(d=>d.mini_y).y(d=>d.mini_x))
                .style("opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", 1);
            this.e_shadow_links.enter()
                .append("path")
                .attr("class", "mini-highlight")
                .attr("d", d3.linkHorizontal().x(d=>d.mini_y).y(d=>d.mini_x))
                .style("opacity", 0)
                .transition()
                .duration(this.create_ani)
                .delay(this.remove_ani + this.update_ani)
                .style("opacity", d => d.target.mini_selected ? 1: 0);
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
        rest_node_create(){
            // let node_groups = this.e_rest_nodes.enter()
            //     .append("g")
            //     .attr("class", "rest-tree-node")
            //     .attr("id", d => "id-" + d.id)
            //     .attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
            // node_groups.data(d => d.children.reverse());
        },
        update(){
            this.node_update();
            this.set_update();
            this.expand_icon_update();
            this.mini_update();
        },
        node_update(){
            this.tree_node_group
            .transition()
            .duration(this.update_ani)
            .delay(this.remove_ani)
            .attr("transform", () => {
                let x = this.layer_height / 2;
                if (!this.expand_tree){
                    x = 0;
                }
                return "translate(" + x + ", " 
                + (this.text_height + this.layer_height / 2) + ")"
            });
            this.e_nodes
            .transition()
            .duration(this.update_ani)
            .delay(this.remove_ani)
            .attr("transform", d => "translate(" + d.x + ", " + d.y + ")");
            this.e_nodes.select("rect.background")
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("x", this.layer_height / 4)
                .attr("y", - this.layer_height * 0.8 / 2)
                .attr("height", this.layer_height * 0.8)
                .attr("width", () => {
                    // return Global.getTextWidth(d.data.name, "16px Roboto, sans-serif") + this.layer_height / 2; 
                    return this.max_text_width;
                });
            
            this.e_nodes.select("path.icon")
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("d", function(d){
                    return Global.node_icon(0, 0, d.type);
                })
                .style("opacity", () => this.expand_tree ? 1 : 0);
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

            let bars = this.e_nodes.select("g.node-bars")
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("transform", () => "translate(" + (this.max_text_width - 15) + 
                    ", " + (- (this.bar_height - this.rounded_r) / 2) + ")");
            bars.select("path.bar-precision")
                .attr("d", d => Global.half_rounded_rect(0, (1 - d.data.precision) * this.bar_height,
                    this.bar_width, d.data.precision * this.bar_height, this.rounded_r, 0));
            bars.select("path.bar-recall")
                .attr("d", d => Global.half_rounded_rect(this.bar_width, (1 - d.data.recall) * this.bar_height, 
                    this.bar_width, d.data.recall * this.bar_height, 0, this.rounded_r));

                
        },
        mini_update(){
            this.e_mini_nodes
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("cx", d => d.mini_y)
                .attr("cy", d => d.mini_x);
            this.e_mini_links
                .transition()
                .duration(this.update_ani)
                .delay(this.remove_ani)
                .attr("d", d3.linkHorizontal().x(d=>d.mini_y).y(d=>d.mini_x));
            this.e_shadow_links
                .transition()
                .duration(d => d.target.mini_selected ? this.create_ani : this.update_ani)
                .delay(d => d.target.mini_selected ? this.update_ani + this.remove_ani : this.remove_ani)
                .attr("d", d3.linkHorizontal().x(d=>d.mini_y).y(d=>d.mini_x))
                .style("opacity", d => d.target.mini_selected ? 1: 0);

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
        rest_node_update(){

        },
        remove(){
            this.e_nodes.exit()
                .remove();
            this.e_sets.exit()
                .remove();
            this.e_set_links.exit()
                .remove();
            this.mini_remove();
        },
        node_remove(){

        },
        mini_remove(){

        },
        rest_node_remove(){

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
        this.text_height = this.bbox_height * 0.06; 

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
        this.bar_width = 8;
        this.bar_height = this.layer_height * 0.45
        this.rounded_r = 3;

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
            .attr("transform", "translate(" + (5) + ", " + (this.text_height * 0.8) + ")");
        this.tree_node_group = this.svg.append("g")
            .attr("id", "tree-node-group")
            .attr("transform", "translate(" + 2 + ", " + (this.layout_height / 2) + ")");
        this.rest_node_group = this.svg.append("g")
            .attr("id", "rest-node-group")
            .attr("transform", "translate(" + 2 + ", " + (this.layout_height / 2) + ")");    
        this.mini_tree_node_group = this.svg.append("g")
            .attr("id", "mini-tree-node-group")
            .attr("transform", "translate(" + this.mini_tree_x + ", " + this.mini_tree_y + ")");
        this.mini_tree_link_group = this.svg.append("g")
            .attr("id", "mini-tree-link-group")
            .attr("transform", "translate(" + this.mini_tree_x + ", " + this.mini_tree_y + ")");
        this.mini_shadow_link_group = this.svg.append("g")
            .attr("id", "mini-shadow-link-group")
            .attr("transform", "translate(" + this.mini_tree_x + ", " + this.mini_tree_y + ")");
        this.set_group = this.svg.append("g")
            .attr("id", "set-group")
            .attr("transform", "translate(" + 0 + ", " + (this.text_height) + ")");
        this.set_link_group = this.svg.append("g")
            .attr("id", "set-link-group")
            .attr("transform", "translate(" + 0 + ", " + (this.text_height) + ")");

        this.tree_layout = new tree_layout([this.node_width, this.layer_height], this.layout_height);

        this.mini_tree_layout = new mini_tree_layout([this.mini_tree_width, 
            this.mini_tree_height]);

        this.treecut_class = new TreeCut(this.layer_height * 5, this.layout_height, this.layer_height);

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

.mini-tree-node{
    fill: #dfdfdf;
}

.bar-background{
    fill: white;
    stroke: rgb(127, 127, 127);
}

.bar-line{
    fill: rgb(127, 127, 127);
}

.bar-precision{
    fill: rgb(201, 130, 206);
}

.bar-recall{
    fill: rgb(79, 167, 255);
}

.mini-tree-link{
    stroke: #dfdfdf;
    fill: none;
}

/* .mini-shadow-link{
    stroke:
} */

.mini-highlight{
    stroke: #5f5f5f;
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