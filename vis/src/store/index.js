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
        server_url: 'http://166.111.80.151:20211',
        // action trail
        history: [],
        image_num: 0,
        current_id: 0,
        tree: {},
        expand_tree: true,
        focus_node: null,
        set_list: [],
        words: [],
        focus_word: null,
        text_list: [],
        focus_text: null,
        image_list: [],
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
        set_hypergraph_data(state, hypergraph_data){
            console.log("set hypergraph data");

            // process tree 
            state.tree = d3.hierarchy(hypergraph_data.tree,
                function(d){
                    let children = d.children;
                    // console.log("children", children);
                    // return children ? children : undefined;
                    return children
                });
            function unique(arr){
                return Array.from(new Set(arr));
            }
            state.tree.eachAfter(element => {
                element.id = element.data.id;
                element.full_name = element.data.name;
                element.name = element.data.abbr_name;
                // all_children: all children
                // children: children that are visible
                // _children: children that are invisible
                element.all_children = element.children;
                if(element.children) element.children.forEach((d,i) => d.siblings_id = i);
                element._children = [];
                element._total_width = 0;
                if (!element.data.sets){
                    let arr = element.children.map(d => d.data.sets);
                    element.data.sets = unique(Array.prototype.concat.call(...arr));
                }
                if (!element.data.precision){
                    let s = element.all_children.map(d=>d.data.precision);
                    if (s) element.data.precision = s.reduce((a,c)=>{return a+c}, 0) / s.length;
                }
                if (!element.data.recall){
                    let s = element.all_children.map(d=>d.data.recall);
                    if (s) element.data.recall = s.reduce((a,c)=>{return a+c}, 0) / s.length;
                }
                element.api = 2 - (element.data.precision * 2 + element.data.recall) / 2;
                // if (!element.data.words){
                //     let arr = element.children.map(d => d.data.words);
                //     element.data.words = unique(Array.prototype.concat.call(...arr));
                // }
                // element.words = element.data.words.map(d => {
                //     let res = {};
                //     res.text = d[0];
                //     res.value = d[1];
                //     res.cat_id = element.data.cat_id;
                //     res.id = element.data.id;
                //     return res;
                // });
                // element.words = element.words.slice(0, 20);
            });

            state.tree.eachBefore((d, i) => d.order = i);

            state.tree.all_descendants = state.tree.descendants();
            
            // process set
            state.set_list = hypergraph_data.set_list

            console.log("state.tree", state.tree)
            // this.commit("set_focus_node", state.tree);
            console.log("state.focus_node", state.focus_node);
            state.set_list = hypergraph_data.set_list;
        },
        set_history_data(state, history_data) {
            console.log("set history data");
            state.history = history_data;
        },
        set_focus_node(state, nodes) {
            console.log("set focus node");
            state.focus_node = nodes;
        },
        set_expand_tree(state, node){
            console.log("set expand tree");
            state.expand_tree = node;
        },
        set_words(state, words){
            console.log("set words");
            state.words = words.map(d => {
                let res = {};
                res.text = d[0];
                res.value = d[1];
                // res.cat_id = element.data.cat_id;
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
            const resp = await axios.post(`${state.server_url}/hybrid/GetManifest`, {"dataset": key}, 
                {headers: {
                    "Content-Type":"application/json",
                    "Access-Control-Allow-Origin": "*",
                }});
            // console.log(resp);
            commit("set_manifest_data", JSON.parse(JSON.stringify(resp.data)));
        },
        async fetch_hypergraph({commit, state}, key){
            console.log("fetch_hypergraph");
            const resp = await axios.post(`${state.server_url}/hybrid/HyperGraph`, {word: key}, 
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
        async fetch_word({commit, state}, query){
            console.log("fetch_word", query);
            // let query = {
            //     "tree_node_id": key.cat_id,
            //     "match_type": key.text
            // }
            const resp = await axios.post(`${state.server_url}/text/GetWord`, {query}, {headers: {"Access-Control-Allow-Origin": "*"}});
            commit("set_words", JSON.parse(JSON.stringify(resp.data)));
        }
    },
    modules:{
        // empty
    }
})

export default store