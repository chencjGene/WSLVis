import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import * as d3 from "d3"

axios.defaults.headers.common['Access-Control-Allow-Origin'] = '*';

//mount Vuex
Vue.use(Vuex)

//create VueX
const store = new Vuex.Store({
    state:{
        server_url: 'http://localhost:20211',
        // action trail
        history: [],
        image_num: 0,
        current_id: 0,
        tree: {},
        use_treecut: true,
        image_cluster_list: [],
        mismatch: [],
        vis_image_per_cluster: {},
        expand_tree: true,
        expand_set_id: -1,
        grid_data: [],
        nav_id: [],
        label_layout_mode: null,
        cluster_association_mat: [],
        focus_node: null,
        selected_node: {
            node_ids: [],
            nodes: [], 
            curr_full_name: ''
        },
        all_sets: [],
        words: [],
        focus_word: null,
        focus_image: null,
        text_list: [],
        focus_text: null,
        image_list: [],
        selected_flag: [],
        tooltip: {
          top: 0,
          left: 0,
          show: false,
          width: 0,
          content: '',
        }
    },
    getters: {
        
    },
    mutations:{
        edit(state){ // for DEBUG
            state.name = "hello 2";
        },
        set_manifest_data(state, manifest_data){
            console.log("set manifest data");
            state.image_num = manifest_data.image_num;
        },
        set_selected_flag(state, tree){
            console.log("set tree");
            state.tree = tree;
            state.selected_flag = state.tree.all_descendants.map(d => d.selected_flag);
        },
        set_hypergraph_data(state, hypergraph_data){
            console.log("set hypergraph data");
            console.log("hypergraph_data", hypergraph_data);
            console.log("state", state);
            this.commit("set_text_tree_data", hypergraph_data.text_tree);
            this.commit("set_image_cluster_list_data", hypergraph_data.image_cluster_list);
            this.commit("set_cluster_association_mat", hypergraph_data.cluster_association_matrix);
            this.commit("set_mismatch", hypergraph_data.mismatch);
            this.commit("set_vis_image_per_cluster", hypergraph_data.vis_image_per_cluster);
        },
        set_text_tree_data(state, text_tree){
            // process tree 
            state.tree = d3.hierarchy(text_tree,
                function(d){
                    let children = d.children;
                    return children
                });
            state.tree.eachAfter(element => {
                element.id = element.data.id;
                element.full_name = element.data.name;
                element.name = element.full_name;
                if (element.children && element.name !== "root"){
                    element.name = element.children.map(d=>d.name + " ").join("");
                }
                if (element.name.length > 7){
                    element.name = element.name.slice(0,7) + ".";
                }
                

                // all_children: all children
                // children: children that are visible
                // _children: children that are invisible
                element.all_children = element.children;
                if(element.children) element.children.forEach((d,i) => d.siblings_id = i);
                element._children = [];
                element._total_width = 0;
                if (!element.data.precision){
                    let s = element.all_children.map(d=>d.data.precision);
                    if (s) element.data.precision = s.reduce((a,c)=>{return a+c}, 0) / s.length;
                }
                if (!element.data.recall){
                    let s = element.all_children.map(d=>d.data.recall);
                    if (s) element.data.recall = s.reduce((a,c)=>{return a+c}, 0) / s.length;
                }
                element.api = 2 - (element.data.precision * 2 + element.data.recall) / 2;
            });

            state.tree.eachBefore((d, i) => d.order = i);

            state.tree.all_descendants = state.tree.descendants();
            state.tree.all_descendants.forEach(d => d.children = []);
            

            console.log("state.tree", state.tree)

        },
        set_image_cluster_list_data(state, image_cluster_list){
            state.image_cluster_list = image_cluster_list;
            console.log("state.image_cluser_list", state.image_cluster_list);
        },
        set_cluster_association_mat(state, cluster_association_mat){
            state.cluster_association_mat = cluster_association_mat;
            console.log("cluster_association_mat:", state.cluster_association_mat);
        },
        set_mismatch(state, mismatch){
            state.mismatch = mismatch;
            console.log("cluster_association_mat:", state.mismatch);
        },
        set_history_data(state, history_data) {
            console.log("set history data");
            state.history = history_data;
        },
        set_focus_node(state, nodes) {
            console.log("set focus node");
            state.focus_node = nodes;
        },
        set_focus_image(state, image){
            console.log("set focus image");
             state.focus_image = image;
        }, 
        set_selected_node(state, node) {
            console.log("set selected node");
            let index = state.selected_node.node_ids.indexOf(node.id);
            if (index === -1) {
                state.selected_node.node_ids.push(node.id);
                state.selected_node.nodes.push(node);
                d3.selectAll(`#id-${node.id}`).style('stroke', 'black');
            }
            else {
                d3.selectAll(`#id-${node.id}`).style('stroke', '');
                state.selected_node.node_ids.splice(index, 1);
                state.selected_node.nodes.splice(index, 1);
            }
            let new_full_names = [];
            state.selected_node.nodes.forEach(node=>{
                new_full_names.push(node.full_name); 
            });
            state.selected_node.curr_full_name = new_full_names.join('&');
        },
        set_expand_tree(state, node){
            console.log("set expand tree");
            state.expand_tree = node;
        },
        set_expand_set_id(state, id){
            console.log("set expand set id", id);
            state.expand_set_id = id;
        },
        set_words(state, words){
            console.log("set words");
            state.words = words.map(d => {
                let res = {};
                res.text = d[0];
                res.value = d[1];
                // res.id = element.data.id;
                return res;

            });
            state.words = state.words.slice(0, 20);
        },
        set_focus_word(state, word){
            console.log("set focus word");
            state.focus_word = word;
        },
        set_text_list(state, text_list){
            console.log("set text list");
            state.text_list = text_list;
        },
        set_focus_text(state, text){
            console.log("set focus text");
            state.focus_text = text;
        },
        set_vis_image_per_cluster(state, res){
            console.log("set_vis_image_per_cluster", res);
            for(let i in res){
                state.vis_image_per_cluster[i] = res[i];
            }
        },
        set_use_treecut(state, use_treecut){
            state.use_treecut = use_treecut;
        },
        set_grid_layout_data(state, data){
            console.log("set grid layout data", data);
            state.grid_data = data.layout;
            state.nav_id = data.id;
        },
        showTooltip(state, { top, left, width, content }) {
            state.tooltip.top = top 
            state.tooltip.left = left 
            state.tooltip.content = content
            state.tooltip.show = true
            state.tooltip.width = width
        },
        hideTooltip(state) {
            state.tooltip.show = false
        }
    },
    actions:{
        async fetch_manifest({commit, state}, key){
            console.log("fetch_manifest");
            const resp = await axios.post(`${state.server_url}/detection/GetManifest`, key, 
                {headers: {
                    "Content-Type":"application/json",
                    "Access-Control-Allow-Origin": "*",
                }});
            // console.log(resp);
            commit("set_manifest_data", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_hypergraph({commit, state}, key){
            console.log("fetch_hypergraph");
            const resp = await axios.post(`${state.server_url}/detection/HyperGraph`, {word: key}, 
                {headers: 
                    {"Access-Control-Allow-Origin": "*"}});
            commit("set_hypergraph_data", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_history({ commit, state }, key){
            console.log("fetch_history");
            const resp = await axios.post(`${state.server_url}/history/GetHistory`, {word: key}, {headers: {"Access-Control-Allow-Origin": "*"}});
            // console.log(resp);
            commit("set_history_data", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_text({commit, state}, key){
            console.log("fetch_text", key);
            let query = {
                "cat_id": key.cat_id,
                "word": key.text
            }
            const resp = await axios.post(`${state.server_url}/text/GetText`, {query}, {headers: {"Access-Control-Allow-Origin": "*"}});
            commit("set_text_list", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_word({commit, state}){
            console.log("fetch_word");
            let query = {
                tree_node_ids: state.selected_node.node_ids,
                match_type: "p",
            };
            const resp = await axios.post(`${state.server_url}/text/GetWord`, {query}, {headers: {"Access-Control-Allow-Origin": "*"}});
            commit("set_words", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_images({commit, state}, image_cluster_ids){
            console.log("fetch_images", image_cluster_ids);
            const resp = await axios.post(`${state.server_url}/detection/Rank`, image_cluster_ids, {headers: {"Access-Control-Allow-Origin": "*"}});
            commit("set_vis_image_per_cluster", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_grid_layout({commit, state}, query){
            const resp = await axios.post(`${state.server_url}/detection/GridLayout`, query, {headers: {"Access-Control-Allow-Origin": "*"}});
            commit("set_grid_layout_data", JSON.parse(JSON.stringify(resp.data)));
        }
    },
    // computed: {
    //     selected_flag(){
    //         return this.$store.state.tree.all_descendants.map(d => !! d.selected_flag);
    //     }
    // },
    modules:{
        // empty
    }
})

export default store