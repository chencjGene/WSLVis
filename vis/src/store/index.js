import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import * as d3 from "d3"

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
        focus_node: null,
        set_list: []
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
        set_hypergraph_data(state, hypergraph_data){
            console.log("set hypergraph data");

            // process tree 
            state.tree = d3.hierarchy(hypergraph_data.tree,
                function(d){
                    let children = d.children;
                    // return children ? children : undefined;
                    return children
                });
            function unique(arr){
                return Array.from(new Set(arr));
            }
            state.tree.eachAfter(element => {
                element.id = element.data.id;
                element.name = element.data.name;
                // all_children: all children
                // children: children that are visible
                // _children: children that are invisible
                element.all_children = element.children;
                element._children = [];
                element._total_width = 2;
                if (!element.data.sets){
                    let arr = element.children.map(d => d.data.sets);
                    element.data.sets = unique(Array.prototype.concat.call(arr));
                }
            });

            // process set
            state.set_list = hypergraph_data.set_list

            console.log("state.tree", state.tree)
            this.commit("set_focus_node", state.tree);
            console.log("state.focus_node", state.focus_node);
            state.set_list = hypergraph_data.set_list;
        },
        set_history_data(state, history_data) {
            console.log("set history data");
            state.history = history_data;
        },
        set_focus_node(state, node) {
            console.log("set focus node");
            state.focus_node = [node];
        }
    },
    actions:{
        async fetch_manifest({commit, state}, key){
            console.log("fetch_manifest");
            const resp = await axios.post(`${state.server_url}/hybrid/GetManifest`, {"dataset": key});
            // console.log(resp);
            commit("set_manifest_data", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_hypergraph({commit, state}, key){
            console.log("fetch_hypergraph");
            const resp = await axios.post(`${state.server_url}/hybrid/HyperGraph`, {word: key});
            commit("set_hypergraph_data", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_history({ commit, state }, key){
            console.log("fetch_history");
            const resp = await axios.post(`${state.server_url}/history/GetHistory`, {word: key});
            // console.log(resp);
            commit("set_history_data", JSON.parse(JSON.stringify(resp.data)));
        }
    },
    modules:{
        // empty
    }
})

export default store