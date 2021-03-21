<template>
  <v-row class="image-view fill-width mr-0">
    <v-col cols="12" class="topname fill-width"> Image <svg id="btn-svg" width="100px" height="24px"></svg></v-col>
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
      let that = this;
      console.log("triger selected node");
      that.mode = 'grid';
      that.update_data();
      that.update_view();
    }, 
    focus_image(){
      let that = this;
      console.log("triger focus image");
      that.mode = 'focus-image';
      that.update_data();
      that.update_view();
    }, 
    focus_text(){
      let that = this;
      console.log("triger focus text");
      that.mode = 'focus-text';
      that.update_data();
      that.update_view();
    }
  },
  computed: {
    ...mapState(["server_url", "selected_images", "focus_image", "focus_text"])
  },
  methods: {
    ...mapActions(["fetch_text_by_ids"]),
    update_data() {
      let that = this;
      if (that.mode === 'grid') {
        // get data by selected_node
        let data = that.selected_images;
        that.grid_images = data;
        that.grid_images.forEach((d) => {
          let dets = d.data.d;
          let boxes = [];
          for (let i = 0; i < dets.length; i++){
            let x = dets[i][0];
            let w = (dets[i][2] - dets[i][0]);
            let y = dets[i][1];
            let h = (dets[i][3] - dets[i][1]);
            let idx = d.id + "-" + i;
            boxes.push({x, y, w, h, idx});
          }
          d.boxes = boxes;
        });
        that.grid_page = 0;
        let end_num = that.x_grid_num * that.y_grid_num;
        if (that.grid_images.length < end_num) {
          end_num = that.grid_images.length;
        }
        that.grid_images_showing = that.grid_images.slice(0, end_num);
      }
      else if (that.mode === 'focus-image') {
          // one-image mode, focus image
        let aspect_ratio = that.focus_image.h / that.focus_image.w;
        let width = 0;
        let height = 0;
        let image_x = 0;
        let image_y = 0;
        let boxes = [];
        let dets = that.focus_image.d;
        that.dets = dets;
        if (aspect_ratio > that.aspect_ratio){
          height = that.layout_height;
          width = that.layout_height * that.focus_image.w / that.focus_image.h;
          image_x = (that.layout_width - width) / 2;
          image_y = 0;
        }
        else{
          width = that.layout_width;
          height = width * that.focus_image.h / that.focus_image.w;
          image_x = 0;
          image_y = (that.layout_height - height) / 2;
        }
        for (let i = 0; i < dets.length; i++){
          let x = width * dets[i][0] + image_x;
          let w = width * (dets[i][2] - dets[i][0]);
          let y = height * dets[i][1] + image_y;
          let h = height * (dets[i][3] - dets[i][1]);
          let idx = that.focus_image.idx + "-" + i;
          boxes.push({x, y, w, h, idx});
        }
        this.one_image_data = {width, height, "idx": that.focus_image.idx, "x":image_x, "y": image_y};
        this.one_image_box_data = boxes;
      }
      else if (that.mode === 'focus-text') {
          // one-image mode, focus image
        let aspect_ratio = that.focus_text.h / that.focus_text.w;
        let width = 0;
        let height = 0;
        let image_x = 0;
        let image_y = 0;
        let boxes = [];
        let dets = that.focus_text.d;
        that.dets = dets;
        if (aspect_ratio > that.aspect_ratio){
          height = that.layout_height;
          width = that.layout_height * that.focus_text.w / that.focus_text.h;
          image_x = (that.layout_width - width) / 2;
          image_y = 0;
        }
        else{
          width = that.layout_width;
          height = width * that.focus_text.h / that.focus_text.w;
          image_x = 0;
          image_y = (that.layout_height - height) / 2;
        }
        for (let i = 0; i < dets.length; i++){
          let x = width * dets[i][0] + image_x;
          let w = width * (dets[i][2] - dets[i][0]);
          let y = height * dets[i][1] + image_y;
          let h = height * (dets[i][3] - dets[i][1]);
          let idx = that.focus_text.idx + "-" + i;
          boxes.push({x, y, w, h, idx});
        }
        this.one_image_data = {width, height, "idx": that.focus_text.idx, "x":image_x, "y": image_y};
        this.one_image_box_data = boxes;
      }
      
      that.update_view();
      that.show_detail(null, -1);
    },
    update_view() {
      let that = this;
      
      if (that.mode === 'grid') {
        that.one_image_group.style('display', 'none');
        that.one_image_box_group.style('display', 'none');
        that.grid_group.style('display', 'block');
        that.grid_box_group.style('display', 'block');
        that.detail_group.style('display', 'block');
        that.cover_group.style('display', 'block');
          that.e_data = that.svg.selectAll(".one-image")
          .data([that.image_id]);
      }
      else {
        that.one_image_group.style('display', 'block');
        that.one_image_box_group.style('display', 'block');
        that.grid_group.style('display', 'none');
        that.grid_box_group.style('display', 'none');
        that.detail_group.style('display', 'none');
        that.cover_group.style('display', 'none');
          // for one-image, focus image
        that.one_images = that.one_image_group.selectAll(".info-image")
          .data([that.one_image_data], d => d.idx);
        that.one_image_boxes = that.one_image_box_group.selectAll(".info-box")
          .data(that.one_image_box_data, d => d.idx);
      }

      that.create();
      that.update();
      that.remove();
    },
    create() {
      let that = this;
      if (that.mode === 'grid') {
        that.grid_group_g =  that.grid_group.selectAll(".grid-image")
          .data(that.grid_images_showing);
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

        that.cover_group_rect_g = that.cover_group.selectAll(".one-grid-image-rect-g")
          .data(that.grid_images_showing);
        let cover_group_rect_g_enters = that.cover_group_rect_g.enter()
          .append("g")
          .attr("class", "one-grid-image-rect-g")
          .attr("transform", "translate(0,0)");
        cover_group_rect_g_enters.append("rect")
          .attr("class", "one-grid-image-rect")
          .attr("x", (d, i) => that.img_padding + (i % that.x_grid_num) * (that.grid_size + that.grid_offset) - 2)
          .attr("y", (d, i) => that.img_padding + Math.floor(i / that.x_grid_num) * (that.grid_size + that.grid_offset) - 2)
          .attr("width", that.grid_size + 4)
          .attr("height", that.grid_size + 4)
          .attr("fill-opacity", 0)
          .on("click", function(_, d){
              that.show_detail(d, d.index);
          });
        if (that.detail_pos !== -1) {
          that.grid_boxes.enter()
            .append("rect")
            .attr("class", "info-box")
            .attr("x", d => d.data.x * d.image_width + d.image_x)
            .attr("y", d => d.data.y * d.image_height + d.image_y)
            .attr("width", d => d.data.w * d.image_width)
            .attr("height", d => d.data.h * d.image_height)
            .style("fill", "none")
            .style("stroke", Global.BoxRed)
            .style("stroke-width", 1);
        }
      }
      else {
          // one image, focus_image
        that.one_images.enter()
          .append("image")
          .attr("class", "info-image")
          .attr("x", d => d.x)
          .attr("y", d => d.y)
          .attr("width", d => d.width)
          .attr("height", d => d.height)
          .attr("href", d => that.server_url + `/image/origin_image?filename=${d.idx}.jpg`);
        that.one_image_boxes.enter()
          .append("rect")
          .attr("class", "info-box")
          .attr("x", d => d.x)
          .attr("y", d => d.y)
          .attr("width", d => d.w)
          .attr("height", d => d.h)
          .style("fill", "none")
          .style("stroke", Global.BoxRed)
          .style("stroke-width", 1);
      }
    },
    update(){
      let that = this;
      if (that.mode === 'grid'){
        that.e_data.attr("href", d => that.Website + ":" + that.Port + `/image/image?filename=${d.id}.jpg`);
        that.grid_group.selectAll(".one-grid-image").data(that.grid_images_showing).attr("xlink:href", d => that.Website + ":" + that.Port + `/image/image?filename=${d.id}.jpg`);
        that.cover_group.selectAll(".one-grid-image-rect").data(that.grid_images_showing);

        that.grid_group_g.selectAll("rect")
          .transition()
          .duration(that.update_ani);


        that.grid_group_g
          .transition()
          .duration(that.update_ani)
          .attr("transform", (d, i) => "translate(" + 0 + ", " +
              ((that.detail_pos !== -1 && Math.floor(i / that.x_grid_num) >  Math.floor(that.detail_pos / that.x_grid_num)) * (that.img_padding * 3 + that.img_size)) + ")");
        that.cover_group_rect_g
          .transition()
          .duration(that.update_ani)
          .attr("transform", (d, i) => "translate(" + 0 + ", " +
              ((that.detail_pos !== -1 && Math.floor(i / that.x_grid_num) >  Math.floor(that.detail_pos / that.x_grid_num)) * (that.img_padding * 3 + that.img_size)) + ")");
        if (that.detail_pos !== -1) {
          that.grid_boxes
            .transition()
            .duration(that.update_ani)
            .attr("x", d => d.data.x * d.image_width + d.image_x)
            .attr("y", d => d.data.y * d.image_height + d.image_y)
            .attr("width", d => d.data.w * d.image_width)
            .attr("height", d => d.data.h * d.image_height)
            .style("fill", "none")
            .style("stroke", Global.BoxRed)
            .style("stroke-width", 1);
        }
      }
      else {
        that.one_images
          .attr("width", d => d.width)
          .attr("height", d => d.height)
          .attr("href", d => that.server_url + `/image/origin_image?filename=${d.idx}.jpg`);
      }
      
    },
    remove(){
      let that = this;
      if (that.mode === 'grid') {
        that.grid_group_g
          .exit()
          .remove();
        that.cover_group_rect_g
          .exit()
          .remove();
        if (that.detail_pos !== -1) {
          that.grid_boxes.exit()
            .remove();
        }
      }
      else {
        that.one_images.exit()
          .remove();
        that.one_image_boxes.exit()
          .remove();
          
        setTimeout(()=>{
          let bbox = that.one_image_group.node().getBoundingClientRect();
          that.svg
            .transition()
            .duration(that.update_ani)
            .attr("height", bbox.height + that.one_image_data.y);
        }, that.update_ani);
      }
    }, 
    show_detail(d, i){
      let that = this;
      that.selected_id = d ? [d.id] : [];
      
      if(i===-1){
        that.detail_pos = -1;
        that.detail_group.style("opacity", 0);
        that.detail_group.selectAll("image").remove();
        that.detail_group.append("image");
        that.grid_box_group.style("opacity", 0);
        that.grid_box_group.selectAll("rect").remove();
      }
      else {
        let img_url = that.Website + ":" + that.Port + `/image/origin_image?filename=${d.id}.jpg`;
        console.log("show detail:", that.detail_pos, img_url);
        that.layout_width = parseFloat(that.svg.attr("width"));
        let x_padding = (that.layout_width - that.img_size) / 2;
        let _y = that.img_padding + (Math.floor(i / that.x_grid_num) + 1) * (that.grid_size + that.grid_offset);
        let aspect_ratio = d.data.h / d.data.w
        let image_width = that.img_size, image_height = that.img_size, image_x = x_padding, image_y = _y;
        if (aspect_ratio >= 1) {
          image_width /= aspect_ratio;
          image_x += (that.img_size - image_width) / 2;
        }
        else {
          image_height *= aspect_ratio;
          image_y += (that.img_size - image_height) / 2;
        }
        if (that.detail_pos === -1) {
          that.detail_pos = i;
          that.detail_group.transition()
            .duration(that.update_ani)
            .style("opacity", 1);
          that.grid_box_group.transition()
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
            .attr("width", that.img_size)
            .attr("height", that.img_size);
          that.grid_boxes = that.grid_box_group.selectAll(".info-box")
            .data(d.boxes.map(_d=>{
              return {
                idx: _d.idx,
                data: _d,
                image_x: image_x,
                image_y: image_y, 
                image_width: image_width, 
                image_height: image_height
              };
            }), _d => _d.idx);
          that.grid_box_group.select("image")
            .attr("xlink:href", img_url)
            .attr("x", that.img_padding)
            .attr("y", _y)
            .attr("width", 0)
            .attr("height", 0)
            .transition()
            .duration(that.update_ani)
            .attr("x", x_padding)
            .attr("y", _y)
            .attr("width", that.img_size)
            .attr("height", that.img_size);
          that.update_view();
        } 
        else if (that.detail_pos === i) {
          that.detail_pos = -1;
          that.detail_group.transition()
            .duration(that.update_ani)
            .style("opacity", 0);
          that.grid_box_group.style("opacity", 0);
          that.grid_box_group.selectAll("rect").remove();
          that.detail_group.select("image")
            .transition()
            .duration(that.update_ani)
            .attr("x", x_padding)
            .attr("y", _y)
            .attr("width", 0)
            .attr("height", 0);
          that.update_view();
        } 
        else {
          that.detail_pos = i;
          that.detail_group.transition()
            .duration(that.update_ani)
            .style("opacity", 1);
          that.grid_box_group.transition()
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
          that.grid_boxes = that.grid_box_group.selectAll(".info-box")
            .data(d.boxes.map(_d=>{
              return {
                idx: _d.idx,
                data: _d,
                image_x: image_x,
                image_y: image_y, 
                image_width: image_width, 
                image_height: image_height
              };
            }), _d => _d.idx);
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
            .attr("width", that.img_size)
            .attr("height", that.img_size);
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
      
    },
    change_grid_page(direction) {
      let that = this;
      let start_num = that.x_grid_num * that.y_grid_num * (that.grid_page + direction);
      if (start_num >= 0 && start_num <that.grid_images.length) {
        that.grid_page += direction;
        let end_num = start_num + that.x_grid_num * that.y_grid_num;
        if (that.grid_images.length < end_num) {
          end_num = that.grid_images.length;
        }
        that.grid_images_showing = that.grid_images.slice(start_num, end_num);
        that.update_view();
        that.show_detail(null, -1);
      }
    }
  },
  async mounted() {
    window.image = this;
    let that = this;
    let container = d3.select(".image-content");
    // console.log("container", container);
    container.style('height', `${Global.WindowHeight * 0.34 - 24}px`);
    let bbox = container.node().getBoundingClientRect();
    that.width = bbox.width;
    that.height = bbox.height;
    that.layout_width = that.width - 20;
    that.layout_height = that.height;
    that.Website = "http://localhost";
    that.Port = "20211";
    that.img_padding = 10;
    that.grid_page = 0;
    that.x_grid_num = 7;
    that.y_grid_num = 5;
    that.grid_offset = 10;
    that.grid_size = Math.min((that.layout_width - that.grid_offset) / that.x_grid_num, (that.layout_height - that.grid_offset) / that.y_grid_num) - that.grid_offset;
    that.create_ani = Global.Animation / 4;
    that.update_ani = Global.Animation / 4;
    that.remove_ani = Global.Animation / 4;
    that.detail_pos = -1;
    that.mode = 'grid';
    that.grid_images = [];
    that.grid_images_showing = [];
    that.img_grid_urls = [];
    that.aspect_ratio = that.layout_height / that.layout_width;
    that.img_size = 250;

    that.svg = container
      .append("svg")
      .attr("id", "image-svg")
      .attr("width", that.width)
      .attr("height", that.layout_height - 10);

    that.main_group = that.svg
      .append("g")
      .attr("id", "main-group")
      .attr("transform", `translate(10,0)`);

    that.detail_group = that.main_group
      .append("g")
      .attr("id", "detail-group")
      .on("click", () => {
        console.log("detail group");
        that.fetch_text_by_ids(that.selected_id);
      })

    that.grid_group = that.main_group
      .append("g")
      .attr("id", "grid-group");
    
    that.one_image_group = that.main_group
      .append("g")
      .attr("id", "one_image-group");

    that.grid_box_group = that.main_group
      .append("g")
      .attr("id", "grid_box-group");

    that.one_image_box_group = that.main_group
      .append("g")
      .attr("id", "one_image_box-group");

    that.cover_group = that.main_group
      .append("g")
      .attr("id", "cover-group");

    if ((that.grid_offset + that.grid_size) * that.x_grid_num + that.grid_offset < that.layout_width) {
      let delta_x = that.layout_width - (that.grid_offset + that.grid_size) * that.x_grid_num - that.grid_offset;
      that.grid_group.attr("transform", `translate(${delta_x / 2},0)`);
      that.grid_box_group.attr("transform", `translate(${delta_x / 2},0)`);
      that.cover_group.attr("transform", `translate(${delta_x / 2},0)`);
    }
    else {
      let delta_y = that.layout_height - (that.grid_offset + that.grid_size) * that.y_grid_num - that.grid_offset;
      that.grid_group.attr("transform", `translate(0,${delta_y / 2})`);
      that.grid_box_group.attr("transform", `translate(0,${delta_y / 2})`);
      that.cover_group.attr("transform", `translate(0,${delta_y / 2})`);
    }
    let btn_svg = d3.select("#btn-svg");
    let btn_data = [{
      'name': 'left',
      'x': 0
    }, {
      'name': 'right',
      'x': 30
    }];
    let btn_group = btn_svg.append("g")
      .attr("id", "btn-group")
      .attr("transform", `translate(50,0)`);
    let arrows = btn_group.selectAll('.arrow').data(btn_data);
    arrows.enter()
      .append('path')
      .attr('class', 'arrow')
      .attr('d', d=>{
        return Global.get_path_of_page_btn(d.x, 6, 18, 12, d.name);
      })
      .style('stroke', 'black')
      .style('stroke-width', '2px')
      .style('fill', 'none');
    let rects = btn_group.selectAll('.btn-cover-rect').data(btn_data);
    rects.enter()
      .append('rect')
      .attr('class', 'btn-cover-rect')
      .attr('id', d => `btn-cover-rect-${d.name}`)
      .style('x', d=>d.x - 2)
      .style('y', 4)
      .style('rx', 4)
      .style('width', 22)
      .style('height', 16)
      .style('stroke', 'none')
      .style('fill', 'black')
      .style('opacity', 0)
      .on('mouseenter', (_, d) => {
        d3.select(`#btn-cover-rect-${d.name}`)
          .transition()
          .duration(that.update_ani)
          .style('opacity', 0.3);
      })
      .on('mouseleave', (_, d) => {
        d3.select(`#btn-cover-rect-${d.name}`)
          .transition()
          .duration(that.update_ani)
          .style('opacity', 0);
      })
      .on('click', (_, d) => {
        if (d.name === 'left') {
          that.change_grid_page(-1);
        }
        else {
          that.change_grid_page(1);
        }
      });
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