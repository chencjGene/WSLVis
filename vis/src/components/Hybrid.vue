<template>  
    <v-col cols="9" class="main-view fill-height">
        <!-- <v-col cols="12" class="topname fill-width">
        </v-col> -->
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
import {mapActions, mapState} from "vuex"
import * as d3 from "d3"
import * as Global from '../plugins/global'
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
           "tree", "set_list" 
        ])
    },
    methods:{
        ...mapActions([
            "fetch_hypergraph"
        ]),
        update_data() {
            console.log("hybrid update data");
            console.log(this.tree);
            const root = this.tree_layout(this.tree);
            this.nodes = root.descendants();
            this.links = root.links();
        },
        update_view() {
            console.log("hybrid update view");

            this.e_nodes = this.tree_node_group.selectAll(".tree-node")
            .data(this.nodes);
            this.e_links = this.tree_link_group.selectAll(".tree-link")
            .data(this.links);

            // TODO: set remove ani when exit is none

            this.remove();
            this.update();
            this.create();
        },
        create(){
            console.log("Global", Global.GrayColor, Global.Animation)
            this.e_nodes.enter()
            .append("g")
            .attr("class", "tree-node")
            .attr("transform", d => "translate(" + d.y + ", " + d.x + ")")
            .append("circle")
            .attr("r", 2)
            .attr("fill", Global.GrayColor)
            .style("opacity", 0)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
            this.e_links.enter()
            .append("path")
            .attr("class", "tree-link")
            .attr("d", d3.linkHorizontal()
                .x(d => d.y)
                .y(d => d.x))
            .style("opacity", 0)
            .style("stroke", Global.GrayColor)
            .style("stroke-width", 1.5)
            .transition()
            .duration(this.create_ani)
            .delay(this.update_ani + this.remove_ani)
            .style("opacity", 1);
        },
        update(){
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
            // console.log(this.tree);
            this.update_data();
            this.update_view();
        }
    },
    async mounted(){
        console.log("hybrid mounted");
        window.hybrid = this;
        let container = d3.select(".main-content");
        let bbox = container.node().getBoundingClientRect();
        self.bbox_width = bbox.width;
        self.bbox_height = bbox.height;
        self.node_width = 20; // TODO
        self.layer_height = 20; // TODO
        this.create_ani = Global.Animation;
        this.update_ani = Global.Animation;
        this.remove_ani = 0;
        this.svg = container.append("svg")
            .attr("id", "main-svg")
            .attr("width", self.bbox_width)
            .attr("height", self.bbox_height);
        this.tree_node_group = this.svg.append("g")
            .attr("id", "tree-node-group")
            .attr("transform", "translate(" + 0 + ", " + 0 + ")");
        this.tree_link_group = this.svg.append("g")
            .attr("id", "tree-link-group")
            .attr("transform", "translate(" + 0 + ", " + 0 + ")");
        // this.tree_layout = d3.tree()
        //     .nodeSize([self.node_width, self.layer_height]);
        this.tree_layout = data => {
            const root = d3.hierarchy(data);
            return d3.tree().nodeSize([self.node_width, self.layer_height])(root);
        }
    }
}
</script>

<style>
.tree-link{
    fill: none;
}
</style>