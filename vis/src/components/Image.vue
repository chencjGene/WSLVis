<template>
  <v-row class="image-view fill-width mr-0">
    <v-col cols="12" class="topname fill-width"> Image </v-col>
    <v-col cols="12" class="image-content pa-0"> </v-col>
  </v-row>
</template>


<script>
  import {mapActions, mapState} from "vuex"
  import * as d3 from 'd3'
  import * as Global from "../plugins/global";
export default {
  name: "DetImage",
  data: () => ({}),
  watch: {
    selected_images(){
      console.log("xsx triger selected node");
      this.update_data();
      this.update_view();
    }
  },
  computed: {
    ...mapState(["server_url", "selected_images"])
  },
  methods: {
    ...mapActions([]),
    update_data() {
      let that = this;
      // get data by selected_node
      let data = that.selected_images;
      console.log('xsxsxsxsx');
      that.grid_images = data;
      that.update_view();
      that.show_detail(null, -1);
    },
    update_view() {
      let that = this;
      that.e_data = that.svg.selectAll(".one-image")
        .data([that.image_id]);
      that.create();
      that.update();
      that.remove();
    },
    create() {
      let that = this;
      that.grid_group_g =  that.grid_group.selectAll(".grid-image")
          .data(that.grid_images);
      that.grid_group.selectAll("image").data(that.img_grid_urls);
      that.grid_group.selectAll("rect").data(that.img_grid_urls);
      let grid_group_enters = that.grid_group_g.enter()
          .append("g")
          .attr("class", "grid-image")
          .attr("transform", "translate(0,0)");

      grid_group_enters.append("image")
          .attr("class", "one-grid-image")
          .attr("xlink:href", d => that.Website + ":" + that.Port + `/image/image?filename=${d.id}.jpg`)
          .attr("x", (d, i) => that.img_padding + (i % that.x_grid_num) * (that.grid_size + that.grid_offset))
          .attr("y", (d, i) => that.img_padding + Math.floor(i / that.x_grid_num) * (that.grid_size + that.grid_offset))
          .attr("width", that.grid_size)
          .attr("height", that.grid_size);

      that.cover_group_rect =  that.cover_group.selectAll(".one-grid-image-rect")
          .data(that.grid_images);
      that.cover_group_rect.enter().append("rect")
          .attr("class", "one-grid-image-rect")
          .attr("x", (d, i) => that.img_padding + (i % that.x_grid_num) * (that.grid_size + that.grid_offset) - 2)
          .attr("y", (d, i) => that.img_padding + Math.floor(i / that.x_grid_num) * (that.grid_size + that.grid_offset) - 2)
          .attr("width", that.grid_size + 4)
          .attr("height", that.grid_size + 4)
          .attr("fill-opacity", 0)
          .on("click", function(_, d){
              that.show_detail(d, d.index);
          });
    },
    update(){
      let that = this;
      that.e_data.attr("href", d => that.Website + ":" + that.Port + `/image/image?filename=${d.id}.jpg`);
      that.grid_group.selectAll(".one-grid-image").data(that.grid_images).attr("xlink:href", d => that.Website + ":" + that.Port + `/image/image?filename=${d.id}.jpg`);
      let img_size = 250;

      that.grid_group_g.selectAll("rect")
          .transition()
          .duration(that.update_ani);


      that.grid_group_g
          .transition()
          .duration(that.update_ani)
          .attr("transform", (d, i) => "translate(" + 0 + ", " +
              ((that.detail_pos !== -1 && Math.floor(i / that.x_grid_num) >  Math.floor(that.detail_pos / that.x_grid_num)) * (that.img_padding*3+img_size)) + ")");
      
    },
    remove(){
      let that = this;
      that.grid_group_g
          .exit()
          .remove();
      that.cover_group_rect
          .exit()
          .remove();
    }, 
    show_detail(d, i){
      let that = this;
      if(i===-1){
          that.detail_pos = -1;
          that.detail_group.style("opacity", 0);
          that.detail_group.selectAll("image").remove();
          that.detail_group.append("image");
      }
      else {
          let img_url = that.Website + ":" + that.Port + `/image/origin_image?filename=${d.id}.jpg`;
        console.log("show detail:", that.detail_pos, img_url);
        that.layout_width = parseFloat(that.svg.attr("width"));
        let img_size = 250;
        let x_padding = (that.layout_width - img_size)/2;
        let _y = that.img_padding + (Math.floor(i / that.x_grid_num) + 1) * (that.grid_size + that.grid_offset);
        if (that.detail_pos === -1) {
            that.detail_pos = i;
            that.detail_group.transition()
                .duration(that.update_ani)
                .style("opacity", 1);
            that.detail_group.select("image")
                .attr("xlink:href", img_url)
                .attr("x", that.img_padding)
                .attr("y", _y)
                .attr("width", 0)
                .attr("height", 0)
                .transition()
                .duration(that.update_ani)
                .attr("x", x_padding)
                .attr("y", _y)
                .attr("width", img_size)
                .attr("height", img_size);
            that.update_view();
        } else if (that.detail_pos === i) {
            that.detail_pos = -1;
            that.detail_group.transition()
                .duration(that.update_ani)
                .style("opacity", 0);
            that.detail_group.select("image")
                .transition()
                .duration(that.update_ani)
                .attr("x", x_padding)
                .attr("y", _y)
                .attr("width", 0)
                .attr("height", 0);
            that.update_view();
        } else {
            that.detail_pos = i;
            that.detail_group.transition()
                .duration(that.update_ani)
                .style("opacity", 1);
            that.detail_group.select("image")
                .attr("xlink:href", img_url)
                .transition()
                .duration(that.update_ani)
                .attr("x", x_padding)
                .attr("y", _y)
                .attr("width", 0)
                .attr("height", 0)
                .on("end", function () {
                    let image = d3.select(this);
                    image.remove();
                });
            that.detail_group.append("image")
                .attr("xlink:href", img_url)
                .attr("x", that.img_padding)
                .attr("y", _y)
                .attr("width", 0)
                .attr("height", 0)
                .transition()
                .duration(that.update_ani)
                .attr("x", x_padding)
                .attr("y", _y)
                .attr("width", img_size)
                .attr("height", img_size);
            that.update_view();
        }
      }
      setTimeout(()=>{
        let bbox = that.main_group.node().getBoundingClientRect();
        that.svg
          .transition()
          .duration(that.update_ani)
          .attr("height", bbox.height + 10);
      }, that.update_ani);
      
    }
  },
  async mounted() {
    window.image = this;
    let container = d3.select(".image-content");
    // console.log("container", container);
    container.style('height', `${Global.WindowHeight * 0.34 - 24}px`);
    let bbox = container.node().getBoundingClientRect();
    this.width = bbox.width;
    this.height = bbox.height;
    this.layout_width = this.width - 20;
    this.layout_height = this.height - 10;
    this.Website = "http://localhost";
    this.Port = "20211";
    this.img_padding = 10;
    this.grid_size = 50;
    this.grid_offset = 10;
    this.x_grid_num = parseInt((this.layout_width - 5) / (this.grid_offset + this.grid_size));
    this.create_ani = Global.Animation / 4;
    this.update_ani = Global.Animation / 4;
    this.remove_ani = Global.Animation / 4;
    this.detail_pos = -1;

    this.grid_images = [];
    this.img_grid_urls = [];

    this.svg = container
      .append("svg")
      .attr("id", "image-svg")
      .attr("width", this.width)
      .attr("height", this.layout_height);

    this.main_group = this.svg
      .append("g")
      .attr("id", "main-group");

    this.detail_group = this.main_group
      .append("g")
      .attr("id", "detail-group");

    this.grid_group = this.main_group
      .append("g")
      .attr("id", "grid-group");

    this.box_group = this.main_group
      .append("g")
      .attr("id", "box-group");

    this.cover_group = this.main_group
      .append("g")
      .attr("id", "cover-group");

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
    /* height: calc(100% - 24px); */
    overflow-y: auto;
    overflow-x: hidden;
}
</style>