<template>
  <v-app style="position: relative;">
    <v-main>
        <v-container fluid class="main-background fill-height pa-0">
          <app-detection></app-detection>
          <v-col cols="3" class="other-view fill-height">
            <!-- <app-action-trail></app-action-trail> -->
            <app-text></app-text>
            <app-image></app-image>
          </v-col>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import {mapActions} from "vuex"
// import ActionTrail from './components/ActionTrail.vue'
import CapText from './components/Text.vue'
import DetImage from './components/Image.vue'
import Detection from "./components/Detection.vue"
export default {
  name: 'App', 
  components:{
    // "app-action-trail": ActionTrail,
    "app-detection": Detection,
    "app-text": CapText,
    "app-image": DetImage,
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
    await this.$store.dispatch("fetch_manifest", 
    {"step": "step1", "dataset": "COCO17"});
    await this.$store.dispatch("fetch_hypergraph", 1);
    // await this.$store.dispatch("fetch_grid_layout", {});
    // this.$store.dispatch("fetch_history", 1);
  }
};
</script>

<style>

.main-background {
  height: 100%;
  background-color: #ffffff;
  padding: 0px 0px 0px 0px;
}




/* .action-trail-view {
  height: 33%;
} */


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
/* ::-webkit-scrollbar {display:none;}  */
</style>
