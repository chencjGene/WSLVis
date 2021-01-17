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
        <v-col cols="12" class="main-content pa-0"> </v-col>
    </v-col>
</template>

<script>
// import Vue from "vue"
import { mapActions, mapState, mapMutations } from "vuex";
import * as d3 from "d3";
import * as Global from "../plugins/global";
import {
    mini_tree_layout,
    TreeCut,
    tree_layout,
} from "../plugins/treecut";
import { SetManager } from "../plugins/set_manager";
import TextTree from "../plugins/text_tree";
import TextImageConnection from "../plugins/text_image_connection";
import ImageCards from "../plugins/image_card";
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
            "set_list",
            "focus_node",
            "expand_tree",
            "tooltip",
            "server_url"
        ]),
    },
    methods: {
        ...mapActions(["fetch_hypergraph", "fetch_word"]),
        ...mapMutations([
            "set_focus_node",
            "set_expand_tree",
            "showTooltip",
            "hideTooltip",
            "set_words",
        ]),
        treecut() {
            console.log("detection treecut");
            console.log("before treecut", this.tree);
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
        },
        update_data() {
            console.log("detection update data");
            console.log(this.tree);

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

            // minitree layout
            let mat = this.mini_tree_layout.layout(this.tree);
            this.mini_nodes = mat.nodes;
            this.mini_links = mat.links;

            // set layout
            this.leaf_nodes = this.nodes.filter((d) => d.children.length === 0);
            this.selected_nodes = this.leaf_nodes; // TODO: selected_nodes can be specified by users
            console.log("selected_nodes", this.selected_nodes);
            this.set_manager.update_selected_nodes(this.selected_nodes);
            this.set_manager.update_tree_node_position({
                x: this.tree_node_group_x,
                y: this.tree_node_group_y - this.text_height,
            });
            [this.sets, this.set_links] = this.set_manager.get_sets();
            // this.sets = result.sets;
            // this.set_links = result.set_links;
        },
        update_view() {
            console.log("detection update view");

            this.text_tree_view.sub_component_update(this.nodes, this.rest_nodes);
            this.connection_view.sub_component_update(this.set_links);
            this.image_view.sub_component_update(this.sets);

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
            this.mini_create();
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
        title_create() {
            this.svg
                .append("text")
                .attr("class", "topname")
                .attr("x", this.layer_height / 2)
                .attr("y", this.text_height / 2 + 1)
                .text("Category");
            this.svg
                .append("text")
                .attr("class", "topname")
                .attr("x", this.set_left * 1.05)
                .attr("y", this.text_height / 2 + 1)
                .text("Detection");
        },
        expand_icon_create() {
            this.expanded_icon_group.on("click", () => {
                console.log("click expanded icon", this.expand_tree);
                this.set_expand_tree(!this.expand_tree);
            });
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
                    if (this.expand_tree) {
                        return Global.minus_path_d(0, 0, 10, 10, 2);
                    } else {
                        return Global.plus_path_d(0, 0, 10, 10, 2);
                    }
                });
        },
        update() {
            this.expand_icon_update();
            this.mini_update();
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
                    d3
                        .linkHorizontal()
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
            this.expanded_icon_group
                .selectAll("path")
                .data([this.expand_tree])
                .attr("d", () => {
                    if (this.expand_tree) {
                        return Global.minus_path_d(0, 0, 10, 10, 2);
                    } else {
                        return Global.plus_path_d(0, 0, 10, 10, 2);
                    }
                });
        },
        remove() {
            this.mini_remove();
        },
        mini_remove() {},
    },
    watch: {
        tree() {
            console.log("tree update");
            this.treecut();
            console.log("offset", this.offset);
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
    },
    async mounted() {
        console.log("detection mounted");
        window.detection = this;
        let container = d3.select(".main-content");
        let bbox = container.node().getBoundingClientRect();
        this.bbox_width = bbox.width;
        this.bbox_height = bbox.height;

        // text position
        this.text_height = this.bbox_height * 0.06;

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
        this.set_height = 144;
        this.set_left = this.layer_height * 3 + 200;
        this.set_width = this.layout_width - this.set_left;
        this.set_margin = 6;
        this.image_height = this.set_height * 0.9;
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
        this.title_create();
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

        this.set_manager = new SetManager(
            this.max_text_width + this.layer_height / 4
        );
        this.set_manager.update_layout({
            layout_width: this.layout_width,
            layout_height: this.layout_height,
            set_left: this.set_left,
            set_width: this.set_width,
            set_margin: this.set_margin,
            set_height: this.set_height,
            image_height: this.image_height,
            image_margin: this.image_margin,
        });

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
</style>