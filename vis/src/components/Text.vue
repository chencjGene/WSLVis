<template>
  <v-row class="text-view fill-width mr-0">
    <v-col cols="12" class="topname fill-width"> Text </v-col>
    <v-col cols="12" class="text-content pa-0"> </v-col>
  </v-row>
</template>


<script>
import { mapState, mapActions } from "vuex";
import * as d3 from "d3";
import * as Global from '../plugins/global'
import { wordcloud } from "../plugins/wordcloud.js";
export default {
  name: "CapText",
  data: () => ({}),
  computed: {
    ...mapState(["words", "text_list"]),
  },
  watch: {
    words() {
      console.log("triger words");
      this.update_data();
      this.update_view();
    },
    text_list() {
      this.update_data();
      this.update_view();
    },
  },
  methods: {
    ...mapActions([]),
    update_data() {
      this.min_value = Math.min(...this.words.map(d => d.value));
      this.max_value = Math.max(...this.words.map(d => d.value));
      this.sizeScale = d3.scaleSqrt([this.min_value, this.max_value], [10, 30]);
      this.texts = wordcloud()
        .size([this.wordcloud_width, this.wordcloud_height])
        .data(Global.deepCopy(this.words))
        .padding(4)
        .font(this.fontFamily)
        .fontSize(d => this.sizeScale(d.value))
        .start();
    },
    update_view() {

    },
  },
  async mounted() {
    window.text = this;
    let container = d3.select(".text-content");
    // console.log("container", container);
    let bbox = container.node().getBoundingClientRect();
    this.bbox_width = bbox.width;
    this.bbox_height = bbox.height;
    this.layout_width = this.bbox_width - this.margin_horizonal * 2;
    this.layout_height = this.bbox_height * 0.98;

    // wordcloud
    this.wordcloud_height = this.layout_height * 0.3;
    this.wordcloud_width = this.layout_width;
    this.fontFamily = "Arial";


    this.svg = container
      .append("svg")
      .attr("id", "text-svg")
      .attr("width", this.bbox_width)
      .attr("height", this.layout_height);
  },
};
</script>

<style scoped>
.text-view {
  height: 66%;
}

.text-content {
  border: 1px solid #c1c1c1;
  border-radius: 5px;
  height: calc(100% - 32px);
  margin-bottom: 10px;
}
</style>