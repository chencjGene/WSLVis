<template>  
    <v-col cols="9" class="main-view fill-height">
        <v-col cols="12" class="topname fill-width" id="main-topname">
            <span>
            Hybrid
            </span>
            <!-- <v-btn x-small
            class="ma-2"
            :depressed="true"
            :loading="loading"
            :disabled="loading"
            color="#D1D1D1"
            @click="loader = 'loading'"
            >
            Load
            <template v-slot:loader>
                <v-progress-circular
                :size="18"
                :width="2"
                color="gray"
                indeterminate
                ></v-progress-circular>
            </template> -->
            <!-- </v-btn> -->
        </v-col>
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
    name: "Hybrid",
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
           "tree", "set_list", "focus_node" 
        ])
    },
    methods:{
        ...mapActions([
            "fetch_hypergraph"
        ]),
        ...mapMutations([
            "set_focus_node"
        ]),
        treecut() {
            console.log("hybrid treecut");
            console.log("before treecut", this.tree);
            this.offset = this.treecut_class
                .treeCut(this.focus_node, this.tree, this.tree_layout.layout);
            console.log("after treecut", this.tree);
        },
        update_data() {
            console.log("hybrid update data");
            console.log(this.tree);
            const root = this.tree_layout.layout(this.tree);
            this.nodes = root.descendants();
            this.links = root.links();
            this.leaf_nodes = this.nodes.filter(d => d.children.length == 0);
            console.log("leaf_nodes", this.leaf_nodes);
            this.set_manager.update_leaf_nodes(this.leaf_nodes);
            this.set_manager.update_tree_root(2, this.layout_height / 2 - this.offset);
            let result = this.set_manager.get_sets();
            this.sets = result.sets;
            this.set_links = result.set_links;
        },
        update_view() {
            console.log("hybrid update view");

            this.e_nodes = this.tree_node_group.selectAll(".tree-node")
            .data(this.nodes); //TODO: id map
            this.e_links = this.tree_link_group.selectAll(".tree-link")
            .data(this.links); //TODO: id map
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
            console.log("Global", Global.GrayColor, Global.Animation)
            // node circle
            let node_groups = this.e_nodes.enter()
            .append("g")
            .attr("class", "tree-node")
            .attr("transform", d => "translate(" + d.y + ", " + d.x + ")");
            node_groups
            .append("circle")
            .attr("r", 2)
            .attr("fill", Global.GrayColor)
            .style("opacity", 0)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
            // node name
            node_groups.append("text")
            .text(d => {
                if (d.children && d.children.length > 0){
                    return "";
                }
                else{
                    return d.name;
                }
            })
            .attr("text-anchor", "start")
            .attr("x", 10)
            .attr("dy", ".35em")
            .style("opacity", 0)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
            // link
            this.e_links.enter()
            .append("path")
            .attr("class", "tree-link")
            .attr("d", Global.tree_line)
            .style("opacity", 0)
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 0.5)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);

            this.set_create();

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
            .attr("d", Global.set_line)
            .style("opacity", 0)
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 0.5)
            .style("stroke-dasharray", "5, 5")
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
        },
        update(){
            this.tree_node_group
            .attr("transform", "translate(" + 2 + ", " 
                + (this.layout_height / 2 - this.offset) + ")");
            this.tree_link_group
            .attr("transform", "translate(" + 2 + ", " 
                + (this.layout_height / 2 - this.offset) + ")");
            this.e_nodes
            .transition()
            .duration(this.update_ani)
            .delay(this.remove_ani)
            .attr("transform", d => "translate(" + d.y + ", " + d.x + ")");
            this.e_links
        },
        remove(){
            this.e_nodes
            .exit()
            .remove();
        }
    },
    watch:{
        tree(){
            console.log("tree update");
            this.treecut();
            console.log("offset", this.offset);
            this.update_data();
            this.update_view();
        }
    },
    async mounted(){
        console.log("hybrid mounted");
        window.hybrid = this;
        let container = d3.select(".main-content");
        let bbox = container.node().getBoundingClientRect();
        this.bbox_width = bbox.width;
        this.bbox_height = bbox.height;
        this.layout_width = this.bbox_width;
        this.layout_height = this.bbox_height;
        this.node_width = 50; // TODO
        this.layer_height = 30; // TODO
        this.set_height = 112;
        this.set_left = this.layer_height * 3 + 200;
        this.set_width = this.layout_width - this.set_left;
        this.set_margin = 6;
        this.create_ani = Global.Animation;
        this.update_ani = Global.Animation;
        this.remove_ani = 0;
        this.svg = container.append("svg")
            .attr("id", "main-svg")
            .attr("width", this.layout_width)
            .attr("height", this.layout_height)
            .style("padding-top", "5px");
        this.tree_node_group = this.svg.append("g")
            .attr("id", "tree-node-group")
            .attr("transform", "translate(" + 2 + ", " + (this.layout_height / 2) + ")");
        this.tree_link_group = this.svg.append("g")
            .attr("id", "tree-link-group")
            .attr("transform", "translate(" + 2 + ", " + (this.layout_height / 2) + ")");
        this.set_group = this.svg.append("g")
            .attr("id", "set-group")
            .attr("transform", "translate(" + 0 + ", " + (0) + ")");
        this.set_link_group = this.svg.append("g")
            .attr("id", "set-link-group")
            .attr("transform", "translate(" + 0 + ", " + (0) + ")");
        // this.tree_layout = d3.tree()
        //     .nodeSize([self.node_width, self.layer_height]);
        this.tree_layout = new tree_layout([this.node_width, this.layer_height], 
            function(a, b){
                return a.parent == b.parent ? 1 : 1;
            });

        this.treecut_class = new TreeCut(this.layout_height, this.layer_height * 3);

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
.tree-link{
    fill: none;
}

.set-link{
    fill: none;
}

.main-content {
  background: rgb(242, 246, 255);
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: calc(100% - 24px);
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