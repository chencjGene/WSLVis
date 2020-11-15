<template>
  <v-app style="position: relative;">
    <v-main>
        <v-container fluid class="main-background fill-height pa-0">
          <v-col cols="9" class="main-view fill-height">
            <!-- <v-col cols="12" class="topname fill-width">
            </v-col> -->
            <v-col cols="12" class="topname fill-width" id="main-topname">
              <span>
                Hybrid
              </span>
              <v-btn x-small
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
                </template>
              </v-btn>
            </v-col>
            <v-col cols="12" class="main-content pa-0">
            </v-col>
          </v-col>
          <v-col cols="3" class="other-view fill-height">
            <v-row class="action-trail-view fill-width mr-0">
              <v-col cols="12" class="topname fill-width">
                Action Trail
              </v-col>
              <v-col cols="12" class="action-trail-content pa-0">
              </v-col>
            </v-row>
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
export default {
  name: 'App', 
  data: () => ({
    loader: null,
    loading: false
  }),
  methods:{
    add(){
      // this.$store.commit('edit');
      console.log("add data");
      this.$store.dispatch("fetch_history", 1);
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
  mounted(){
    this.add();
  }
};
</script>

<style>

.main-background {
  height: 100%;
  background-color: #ffffff;
  padding: 0px 0px 0px 0px;
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

.main-content {
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: calc(100% - 22px);
}

.action-trail-view {
  height: 33%;
}

.action-trail-content {
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: calc(100% - 32px);
    margin-bottom: 10px;
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
    height: calc(100% - 22px);
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
