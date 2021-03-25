<template>
  <v-row class="text-view fill-width mr-0">

    <v-col cols="12" class="text-content pa-0">
      <v-col class="label-text pa-0 pl-2"> Selected: 
        <span id="selected-class-name">{{selected_node.curr_full_name}} </span>
        </v-col>
      <v-col class="label-text pa-0 pl-2" id="wordcloud-name"> Word cloud: </v-col>
      <v-col class="wordcloud-col pa-0"> </v-col>
      <v-col class="label-text pa-0 pl-2" id="caption-name"> Captions: </v-col>
      <v-col class="text-col pa-0">
        <template>
          <DynamicScroller :items="text_list" 
          :min-item-size="54"
          class="scroller text-col-scroller" style="overflow-y: auto;">
            <template v-slot="{ item, index, active }">
              <DynamicScrollerItem
                :item="item"
                :active="active"
                :size-dependencies="[item.message,]"
                :data-index="index"
              >
                <div class="label-div" :id="item.id">
                  <v-btn
                    class="label-div-btn"
                    disabled
                    elevation="3"
                    x-small
                    v-for="label in ['cat', 'dog']"
                    :key="label"
                  >{{ label }}</v-btn>
                </div>
              <div
                class="text-div" 
                :id="item.id"
                :style="{ 'background' : item.id == current_selected_id ? '#ddd' : '#fff'}"
                @click="onTextItemClick(item.id)"
              >
                <span v-for="(text, index) in item.message.split(' ')" :key="`${item.id}_${index}`"
                  :style="{ 'text-decoration' : focus_word && text == focus_word.text ? 'underline' : 'none' }"
                >
                  {{ text }}
                </span>
              </div>
              </DynamicScrollerItem>
            </template>
          </DynamicScroller>
        </template>
      </v-col>
    </v-col>
  </v-row>
</template>


<script>
import { mapState, mapActions, mapMutations } from "vuex";
import * as d3 from "d3";
import * as Global from "../plugins/global";
import { wordcloud } from "../plugins/wordcloud.js";
//import TextItem from "../components/text_item"
import { DynamicScroller, DynamicScrollerItem } from "vue-virtual-scroller";
import "vue-virtual-scroller/dist/vue-virtual-scroller.css";
// import Text_item from './text_item.vue';

export default {
  name: "CapText",
  data: () => ({
    current_selected_id: null
  }),
  components: {
    ///"text-item": TextItem,
    DynamicScroller: DynamicScroller,
    DynamicScrollerItem: DynamicScrollerItem
  },
  computed: {
    ...mapState(["selected_node", "words", "focus_word", "text_list"]),
  },
  watch: {
    words() {
      console.log("triger words", this.focus_node);
      this.update_data();
      this.update_view();
    },
    focus_word() {
      console.log("triger focus word");
      this.$store.dispatch("fetch_text_by_word_and_cat_ids", {
        "text": this.focus_word.text,
        "cat_id": this.selected_node["node_ids"]
      });
    }
    // text_list() {
    //   console.log("triger text list", this.text_list);
    //   this.update_data();
    //   this.update_view();
    // },
  },
  methods: {
    ...mapActions(["fetch_text_by_word_and_cat_ids", 
      "fetch_single_image_detection_for_focus_text",
      "fetch_text_by_ids"]),
    ...mapMutations(["set_focus_word"]),
    onTextItemClick(id) {
      console.log("onTextItemClick", id);
      this.current_selected_id = id;
      this.fetch_single_image_detection_for_focus_text({
        image_id: id,
      });
    },
    update_data() {
      this.min_value = Math.min(...this.words.map((d) => d.value));
      this.max_value = Math.max(...this.words.map((d) => d.value));
      this.sizeScale = d3.scaleSqrt([this.min_value, this.max_value], [10, 45]);
      this.wordclouds = wordcloud()
        .size([this.wordcloud_width, this.wordcloud_height])
        .data(Global.deepCopy(this.words))
        .padding(4)
        .font(this.fontFamily)
        .fontSize((d) => this.sizeScale(d.value))
        .start();
      // this.wordclouds.then(d => this.wordclouds = d);
    },
    update_view() {
      this.wordcloud_group
        .selectAll(".wordcloud")
        .transition()
        .duration(this.remove_ani)
        // .style("opacity", 0)
        .remove();
      this.e_words = this.wordcloud_group
        .selectAll(".wordcloud")
        .data(this.wordclouds, d=> d.text);
      // this.e_texts = this.text_group.selectAll("cap-text")
      //   .data(this.wordclouds); // for debug
      this.create();
      this.update();
      this.remove();
      this.adapt_wordcloud_height();
    },

    adapt_wordcloud_height() {
      let bbox = this.wordcloud_group.node().getBBox();
      this.wordcloud_group
        .transition()
        .duration(this.update_ani)
        .attr('transform', `translate(${this.wordcloud_left_margin}, ${-bbox.y})`);
      this.wordcloud_svg
        .transition()
        .duration(this.update_ani)
        .attr('height', bbox.height);
      d3.selectAll('.wordcloud-col')
        .transition()
        .duration(this.update_ani)
        .style('height', `${bbox.height}px`);
      d3.selectAll('.text-col')
        .style('height', `calc(100% - ${bbox.height + 120}px)`);
      bbox = this.text_container.node().getBoundingClientRect();
      d3.selectAll('.text-col-scroller')
        .transition()
        .duration(this.update_ani)
        .style('height', `${bbox.height - 10}px`);
    },

    create() {
      this.wordcloud_create();
      this.text_create();
    },
    wordcloud_create() {
      let word_groups = this.e_words
        .enter()
        .append("g")
        .attr("class", "wordcloud")
        .attr("id", (d) => "id-" + d.text)
        .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")")
        .on("click", (ev, d) => {
          console.log("click word", ev, d);
          d3.selectAll(".wordcloud").style("text-decoration", "none");
          d3.select("#id-" + d.text).style("text-decoration", "underline");
          this.set_focus_word(d);
        });
      word_groups
        .append("text")
        .attr("x", 0)
        .attr("y", 0)
        .attr("dx", (d) => d.dx)
        .attr("dy", (d) => d.dy)
        .attr("font-size", (d) => d.size)
        .style("font-family", (d) => d.font)
        .text((d) => d.text);
      word_groups
        .attr("opacity", 0)
        .transition()
        .duration(this.create_ani)
        .delay(this.remove_ani + this.update_ani)
        .attr("opacity", 1);

    },
    text_create() {},
    update() {
      this.wordcloud_update();
      this.text_update();
    },
    wordcloud_update() {
      this.e_words
        .transition()
        .duration(this.update_ani)
        .delay(this.remove_ani)
        .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")");
      this.e_words
        .select("text")
        .transition()
        .duration(this.update_ani)
        .delay(this.remove_ani)
        .attr("dx", (d) => d.dx)
        .attr("dy", (d) => d.dy)
        .attr("font-size", (d) => d.size)
        .style("font-family", (d) => d.font)
        // .style("text-decoration", d => {
        //   console.log(this.focus_word, d.text, d.text === this.focus_word.text)
        //   return (this.focus_word) && d.text === this.focus_word.text ? 
        //   "underline": "none"
        // })
        .text((d) => d.text);
    },
    text_update() {},
    remove() {
      this.wordcloud_remove();
      this.text_remove();
    },
    wordcloud_remove() {
      // console.log("wordcloud remove");
      // this.wordcloud_group
      //   .selectAll(".wordcloud")
      //   .transition()
      //   .duration(this.remove_ani)
      //   .style("opacity", 0)
      //   .remove();
    },
    text_remove() {},
  },
  async mounted() {
    window.text = this;
    let wordcloud_container = d3.select(".wordcloud-col");
    let text_container = d3.select(".text-col");
    this.text_container = text_container;
    // console.log("container", container);
    // let bbox = container.node().getBoundingClientRect();
    // this.bbox_width = bbox.width;
    // this.bbox_height = bbox.height;
    // this.layout_width = this.bbox_width;
    // this.layout_height = this.bbox_height * 0.98;
    this.create_ani = Global.Animation / 4;
    this.update_ani = Global.Animation / 4;
    this.remove_ani = Global.Animation / 4;

    // wordcloud
    this.wordcloud_height = wordcloud_container
      .node()
      .getBoundingClientRect().height;
    this.wordcloud_box_width = wordcloud_container
      .node()
      .getBoundingClientRect().width;
    this.wordcloud_width = this.wordcloud_box_width * 0.8;
    this.wordcloud_left_margin = this.wordcloud_box_width * 0.1;
    this.fontFamily = "Arial";

    // text
    this.text_height = text_container.node().getBoundingClientRect().height;
    this.text_width = text_container.node().getBoundingClientRect().width;

    // this.svg = container
    //   .append("svg")
    //   .attr("id", "text-svg")
    //   .attr("width", this.bbox_width)
    //   .attr("height", this.layout_height);
    this.wordcloud_svg = d3
      .select(".wordcloud-col")
      .append("svg")
      .attr("width", this.wordcloud_box_width)
      .attr("height", this.wordcloud_height);
    this.wordcloud_group = this.wordcloud_svg.append("g")
      .attr("id", "wordcloud-group")
      .attr("transform", "translate(" + 0 + ", " + 0 + ")");
    // this.text_group = this.svg.append("g")
    //   .attr("id", "text-group")
    //   .attr("transform", "translate(" + (0) + ", " + (this.wordcloud_height) + ")");
  },
};
</script>

<style>
.text-view {
  height: 66%;
}

.text-content {
  border: 1px solid #c1c1c1;
  border-radius: 5px;
  height: calc(100% - 32px);
  margin: 10px;

}

.label-div-btn {
  margin-left: 5px;
}

.wordcloud{
  cursor: default;
}

.wordcloud-col {
  height: 30%;
  /* border-bottom: 1px solid #888; */
}

.text-col {
  height: calc(70% - 120px);
}

.scroller {
  height: 100%;
}

.label-text {
  font-size: 20px;
  font-weight: 600;
}

#wordcloud-name{
  margin-top: 15px;
}

#caption-name{
  margin-top: 15px;
}
.text-div{
  cursor: pointer;
  font-size: 16px;
  margin-left: 8px;
  margin-right: 8px;
  padding-top: 8px;
  padding-bottom: 8px;
  padding-left: 3px;
  border-bottom: 1px solid #ddd;
  word-break: break-all;
}
.text-div:hover {
  background: #ddd;
}

#selected-class-name{
  color: #428BCA;
  font-weight: 400;

}
</style>