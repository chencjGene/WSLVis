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
// import * as d3 from "d3"
export default {
    name: "Hybrid",
    data: () =>({
    }),
    computed:{
        ...mapState([
           "tree", "set_list" 
        ])
    },
    watch:{
        tree(){
            console.log("tree update");
        }
    },
    methods:{
        ...mapActions([
            "fetch_hypergraph"
        ])
    },
    async mounted(){
        console.log("hybrid mounted");
        window.hybrid = this;
        // let container = d3.select("")
    }
}
</script>

<style scoped>

</style>