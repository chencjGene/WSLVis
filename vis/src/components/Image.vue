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
  name: "Image",
  data: () => ({}),
  watch: {},
  methods: {
    ...mapActions([]),
    update_view() {},
    update_data() {},
  },
  async mounted() {
    window.image = this;
    let container = d3.select(".action-trail-content");
    // console.log("container", container);
    let bbox = container.node().getBoundingClientRect();
    self.bbox_width = bbox.width;
    self.bbox_height = bbox.height;
    self.layout_width = self.bbox_width - self.margin_horizonal * 2;
    self.layout_height = self.bbox_height * 0.98;
    self.svg = container
      .append("svg")
      .attr("id", "action-trail-svg")
      .attr("width", self.bbox_width)
      .attr("height", self.layout_height);
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