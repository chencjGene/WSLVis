<template>
  <v-row class="image-view fill-width mr-0">
    <v-col cols="12" class="topname fill-width"> Image </v-col>
    <v-col cols="12" class="image-content pa-0"> </v-col>
  </v-row>
</template>


<script>
  import {mapActions} from "vuex"
  import * as d3 from 'd3'
export default {
  name: "DetImage",
  data: () => ({}),
  watch: {
    focus_image(){
      console.log("triger focus image");
      this.update_data();
      this.update_view();
    }
  },
  methods: {
    ...mapActions(["focus_image"]),
    update_view() {
      this.create();
      this.update();
      this.remove();
    },
    update_data() {
      let that = this;
      this.focus_image = {
          "idx": 22390,
          "w": 640,
          "h": 427,
          "d": [
            [
              0.3089999854564667,
              0.5090000033378601,
              1.0180000066757202,
              0.9890000224113464,
              0.6930000185966492,
              52
            ],
            [
              0.10899999737739563,
              0.289000004529953,
              0.4059999883174896,
              0.7829999923706055,
              0.6589999794960022,
              58
            ]
          ]
        }
      let aspect_ratio = this.focus_image.h / this.focus_image.w;
      let width = 0;
      let height = 0;
      let boxes = [];
      let dets = this.focus_image.d;
      that.dets = dets;
      if (aspect_ratio > this.aspect_ratio){
        height = that.layout_height;
        width = that.layout_height * this.focus_image.w / this.focus_image.h;
      }
      else{
        width = that.layout_width;
        height = width * this.focus_image.h / this.focus_image.w;
      }
      for (let i = 0; i < dets.length; i++){
          let x = width * dets[i][0];
          let w = width * (dets[i][2] - dets[i][0]);
          let y = height * dets[i][1];
          let h = height * (dets[i][3] - dets[i][1]);
          boxes.push({x, y, w, h});
      }
      this.image_data = {width, height, "idx":this.focus_image.idx};
      this.boxes = boxes;
    },
    create() {

    },
    update(){

    },
    remove(){
      
    }
  },
  async mounted() {
    window.image = this;
    let container = d3.select(".image-content");
    // console.log("container", container);
    let bbox = container.node().getBoundingClientRect();
    this.bbox_width = bbox.width;
    this.bbox_height = bbox.height;
    this.margin_horizonal = 4;
    this.layout_width = this.bbox_width - this.margin_horizonal * 2;
    this.layout_height = this.bbox_height * 0.98;
    this.aspect_ratio = this.layout_height / this.layout_width;

    this.svg = container
      .append("svg")
      .attr("id", "image-svg")
      .attr("width", this.bbox_width)
      .attr("height", this.layout_height);

    this.update_data();
    this.update_view();
  },
};
</script>

<style scoped>
.image-view{
  height: 34%;
}

.image-content {
    border: 1px solid #c1c1c1;
    border-radius: 5px;
    height: calc(100% - 24px);
}
</style>