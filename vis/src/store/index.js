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
        history: null,
        current_id: 0
    },
    getters: {
        
    },
    mutations:{
        edit(state){
            state.name = "hello 2";
        },
        set_history_data(state, history_data) {
            state.history = history_data;
            console.log("set history data");
        }
    },
    actions:{
        async fetch_history({ commit, state }, key){
            const resp = await axios.post(`${state.server_url}/history/GetHistory`, {word: key});
            console.log(resp);
            commit("set_history_data", resp)
        }
    },
    modules:{
        // empty
    }
})

export default store