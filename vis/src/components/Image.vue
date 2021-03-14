<template>
  <v-row class="image-view fill-width mr-0">
    <v-col cols="12" class="topname fill-width"> Image </v-col>
    <v-col cols="12" class="image-content pa-0"> </v-col>
  </v-row>
</template>


<script>
  import {mapActions, mapState} from "vuex"
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
  computed: {
    ...mapState(["server_url", "focus_image"])
  },
  methods: {
    ...mapActions([]),
    update_data() {
      let that = this;
      let aspect_ratio = this.focus_image.h / this.focus_image.w;
      let width = 0;
      let height = 0;
      let image_x = 0;
      let image_y = 0;
      let boxes = [];
      let dets = this.focus_image.d;
      // dets = dets.filter(d => d[5]== 7)
      that.dets = dets;
      if (aspect_ratio > this.aspect_ratio){
        height = that.layout_height;
        width = that.layout_height * this.focus_image.w / this.focus_image.h;
        image_x = (that.layout_width - width) / 2;
        image_y = 0;
      }
      else{
        width = that.layout_width;
        height = width * this.focus_image.h / this.focus_image.w;
        image_x = 0;
        image_y = (that.layout_height - height) / 2;
      }
      for (let i = 0; i < dets.length; i++){
          let x = width * dets[i][0] + image_x;
          let w = width * (dets[i][2] - dets[i][0]);
          let y = height * dets[i][1] + image_y;
          let h = height * (dets[i][3] - dets[i][1]);
          let idx = this.focus_image.idx + "-" + i;
          boxes.push({x, y, w, h, idx});
      }
      this.image_data = {width, height, "idx":this.focus_image.idx, "x":image_x, "y": image_y};
      this.boxes = boxes;
    },
    update_view() {
      this.e_images = this.image_group.selectAll(".info-image")
        .data([this.image_data], d => d.idx);
      this.e_boxes = this.boxes_group.selectAll(".info-box")
        .data(this.boxes, d => d.idx);

      this.create();
      this.update();
      this.remove();
    },
    create() {
      this.e_images.enter()
        .append("image")
        .attr("class", "info-image")
        .attr("x", d => d.x)
        .attr("y", d => d.y)
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("href", d => this.server_url + `/image/origin_image?filename=${d.idx}.jpg`);

      this.e_boxes.enter()
        .append("rect")
        .attr("class", "info-box")
            .attr("x", d => d.x)
            .attr("y", d => d.y)
            .attr("width", d => d.w)
            .attr("height", d => d.h)
            .style("fill", "none")
            .style("stroke", "green")
            .style("stroke-width", 1);


    },
    update(){
      this.e_images
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("href", d => this.server_url + `/image/origin_image?filename=${d.idx}.jpg`);
      
    },
    remove(){
      this.e_images.exit()
        .remove();
      this.e_boxes.exit()
        .remove();
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

    this.image_group = this.svg
      .append("g")
      .attr("id", "info-image-g")
      .attr(
        "transform",
        "translate(" + 5 + ", " + 5 + ")"
        );
    this.boxes_group = this.svg
      .append("g")
      .attr("id", "info-boxes-g")
      .attr(
        "transform",
        "translate(" + 5 + ", " + 5 + ")"
        );
    
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