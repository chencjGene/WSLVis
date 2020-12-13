import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

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
            state.tree = hypergraph_data.tree;
            state.set_list = hypergraph_data.set_list;
        },
        set_history_data(state, history_data) {
            console.log("set history data");
            state.history = history_data;
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