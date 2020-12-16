<template>
  <v-app style="position: relative;">
    <v-main>
        <v-container fluid class="main-background fill-height pa-0">
          <app-hybrid></app-hybrid>
          <v-col cols="3" class="other-view fill-height">
            <app-action-trail></app-action-trail>
            <v-row class="text-view fill-width mr-0">
              <v-col cols="12" class="topname fill-width">
                Text
              </v-col>
              <v-col cols="12" class="text-content pa-0">
              </v-col>
            </v-row>
            <v-row class="image-view fill-width mr-0">
              <v-col cols="12" class="topname fill-width">
                Image
              </v-col>
              <v-col cols="12" class="image-content pa-0">
              </v-col>
            </v-row>
          </v-col>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import {mapActions} from "vuex"
import ActionTrail from './components/ActionTrail.vue'
import Hybrid from "./components/Hybrid.vue"
export default {
  name: 'App', 
  components:{
    "app-action-trail": ActionTrail,
    "app-hybrid": Hybrid
  },
  data: () => ({
  }),
  methods:{
    ...mapActions([
      "fetch_manifest"
    ]),
    resize(){

    },
    add(){
      // this.$store.commit('edit');
      console.log("add data");
      // this.$store.dispatch("fetch_history", 1);
    }
  },
  watch:{
    loader () {
      const l = this.loader
      this[l] = !this[l]

      setTimeout(() => (this[l] = false), 30000)

      this.loader = null
    },
  },
  async mounted(){
    this.resize();
    await this.$store.dispatch("fetch_manifest", "COCO17");
    this.$store.dispatch("fetch_hypergraph", 1);
    this.$store.dispatch("fetch_history", 1);
  }
};
</script>

<style>

.main-background {
  height: 100%;
  background-color: #ffffff;
  padding: 0px 0px 0px 0px;
}




.action-trail-view {
  height: 33%;
}


.text-view {
  height: 33%;
}

.text-content {
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: calc(100% - 32px);
    margin-bottom: 10px;
}

.image-view{
  height: 34%;
}

.image-content {
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: calc(100% - 24px);
}

.custom-loader {
  animation: loader 1s infinite;
  display: flex;
}
@-moz-keyframes loader {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(360deg);
  }
}
@-webkit-keyframes loader {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(360deg);
  }
}
@-o-keyframes loader {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(360deg);
  }
}
@keyframes loader {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(360deg);
  }
}

/* diable scrollbar on the right */
::-webkit-scrollbar {display:none;} 
</style>
