<template>
  <v-row class="image-view fill-width mr-0">

    <v-col cols="12" class="image-content pa-0">
      <v-row>
        <div class="image-legend">
          <div class="confidence-slider">
            <span
                class=""
                v-text="'Confidence ≥ '+confidence/100"
                style="width: 125px;"
              ></span>

            <v-slider
              v-model="confidence"
              max="100"
              style="margin: 0 20px 0 20px; width: 120px; height: 30px"
            ></v-slider>
          </div>
          <div class="bounding-label">
              <span>Category label</span>
              <svg :width="30+selectClass.length*8.1" height="32" style="margin: 0 0 0 0">
                    <rect class="background" rx="3.3333333333333335" ry="3.3333333333333335" x="0" y="0" height="32" :width="30+selectClass.length*8.1" style="fill: rgb(235, 235, 243); fill-opacity: 1;"></rect>
                    <text class="node-name" text-anchor="start" x="15" y="16" font-size="18px" dy=".3em" style="opacity: 1;">{{ selectClass }}</text>
                  </svg>
          </div>
          <div class="edit-legend">
            <svg id="btn-edit" :opacity="mode=='grid'?0:1" v-on:click="beginEditBoundingBox()" height="20px" viewBox="0 0 512 511" width="20px"><rect x="0" width="512" y="0" height="512" fill="black" fill-opacity="0"></rect><path d="m405.332031 256.484375c-11.796875 0-21.332031 9.558594-21.332031 21.332031v170.667969c0 11.753906-9.558594 21.332031-21.332031 21.332031h-298.667969c-11.777344 0-21.332031-9.578125-21.332031-21.332031v-298.667969c0-11.753906 9.554687-21.332031 21.332031-21.332031h170.667969c11.796875 0 21.332031-9.558594 21.332031-21.332031 0-11.777344-9.535156-21.335938-21.332031-21.335938h-170.667969c-35.285156 0-64 28.714844-64 64v298.667969c0 35.285156 28.714844 64 64 64h298.667969c35.285156 0 64-28.714844 64-64v-170.667969c0-11.796875-9.539063-21.332031-21.335938-21.332031zm0 0"/><path d="m200.019531 237.050781c-1.492187 1.492188-2.496093 3.390625-2.921875 5.4375l-15.082031 75.4375c-.703125 3.496094.40625 7.101563 2.921875 9.640625 2.027344 2.027344 4.757812 3.113282 7.554688 3.113282.679687 0 1.386718-.0625 2.089843-.210938l75.414063-15.082031c2.089844-.429688 3.988281-1.429688 5.460937-2.925781l168.789063-168.789063-75.414063-75.410156zm0 0"/><path d="m496.382812 16.101562c-20.796874-20.800781-54.632812-20.800781-75.414062 0l-29.523438 29.523438 75.414063 75.414062 29.523437-29.527343c10.070313-10.046875 15.617188-23.445313 15.617188-37.695313s-5.546875-27.648437-15.617188-37.714844zm0 0"/></svg>
            <svg id="btn-remove" :opacity="mode=='grid'?0:1" v-on:click="removeBoundingBox()" height="20px" viewBox="0 0 74 74" width="20px"><rect x="0" width="80" y="0" height="80" fill="black" fill-opacity="0"></rect><path d="m51.512 71.833h-28.723a4.661 4.661 0 0 1 -4.631-4.3l-2.858-39.146a1 1 0 1 1 1.995-.146l2.854 39.142a2.652 2.652 0 0 0 2.636 2.45h28.727a2.651 2.651 0 0 0 2.635-2.45l2.853-39.142a1 1 0 0 1 2 .146l-2.857 39.142a4.661 4.661 0 0 1 -4.631 4.304z"/><path d="m58.741 29.314h-43.184a3.072 3.072 0 0 1 -3.069-3.068v-4.468a3.072 3.072 0 0 1 3.069-3.068h43.184a3.071 3.071 0 0 1 3.068 3.068v4.468a3.071 3.071 0 0 1 -3.068 3.068zm-43.184-8.6a1.07 1.07 0 0 0 -1.069 1.068v4.468a1.071 1.071 0 0 0 1.069 1.068h43.184a1.07 1.07 0 0 0 1.068-1.068v-4.472a1.069 1.069 0 0 0 -1.068-1.068z"/><path d="m58 20.71h-41.7a1 1 0 0 1 -.944-1.329l5.035-14.464a4.6 4.6 0 0 1 4.338-3.084h24.839a4.6 4.6 0 0 1 4.339 3.084l5.034 14.464a1 1 0 0 1 -.941 1.329zm-40.289-2h38.879l-4.572-13.136a2.6 2.6 0 0 0 -2.45-1.741h-24.839a2.6 2.6 0 0 0 -2.449 1.741z"/><path d="m51.5 20.71h-28.7a1 1 0 0 1 -.944-1.329l3.314-9.515a2.294 2.294 0 0 1 2.165-1.538h19.627a2.293 2.293 0 0 1 2.165 1.538l3.312 9.515a1 1 0 0 1 -.939 1.329zm-27.285-2h25.873l-2.85-8.187a.292.292 0 0 0 -.276-.2h-19.627a.292.292 0 0 0 -.276.2z"/><path d="m27.345 52.7a1 1 0 0 1 -.977-.79 11.029 11.029 0 0 1 18.814-9.887 1 1 0 1 1 -1.457 1.37 8.943 8.943 0 0 0 -6.576-2.842 9.038 9.038 0 0 0 -9.028 9.028 9.133 9.133 0 0 0 .2 1.911 1 1 0 0 1 -.767 1.187.953.953 0 0 1 -.209.023z"/><path d="m37.149 60.6a11.072 11.072 0 0 1 -8.033-3.473 1 1 0 1 1 1.457-1.37 8.944 8.944 0 0 0 6.576 2.843 9.038 9.038 0 0 0 9.028-9.028 9.157 9.157 0 0 0 -.119-1.47 1 1 0 0 1 1.974-.321 11.19 11.19 0 0 1 .145 1.791 11.042 11.042 0 0 1 -11.028 11.028z"/><path d="m40.083 44.563a1 1 0 0 1 -.192-1.98l3.388-.668-.667-3.388a1 1 0 0 1 1.962-.387l.861 4.369a1 1 0 0 1 -.788 1.175l-4.37.86a.918.918 0 0 1 -.194.019z"/><path d="m30.7 61.814a1 1 0 0 1 -.98-.807l-.861-4.369a1 1 0 0 1 .787-1.175l4.37-.86a1 1 0 1 1 .387 1.961l-3.389.668.668 3.389a1 1 0 0 1 -.782 1.179.989.989 0 0 1 -.2.014z"/></svg>
          </div>
          <svg id="btn-svg" width="60px" height="24px" viewBox="40 0 60 24" style="margin-right: 20px">
        </svg>
        </div>



      </v-row>
      <svg id="image-svg">
              </svg>
    </v-col>
  </v-row>
</template>


<script>
  import {mapActions, mapMutations, mapState} from "vuex"
  import * as d3 from 'd3'
  import * as d3ContextMenu from "d3-context-menu"
  import * as Global from "../plugins/global";
export default {
  name: "DetImage",
  data: () => ({
    confidence: 50,
    selectRect: null,
    mode: "grid",
    isEditing: false,
    selectClass: ""
  }),
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
    },
    confidence(){
      console.log("confidence change");
      // this.one_image_boxes_threshold = this.confidence / 100;
      this.set_one_image_boxes_threshold(this.confidence / 100);
      this.update_data();
      this.update_view();
    }
  },
  computed: {
    ...mapState(["server_url", "selected_images", 
      "focus_image", "focus_text", "one_image_boxes_threshold"])
  },
  methods: {
    ...mapActions(["fetch_text_by_ids"]),
    ...mapMutations(["set_one_image_boxes_threshold"]),
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
        // let label = -1;
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
          let conf = dets[i][4];
          let idx = that.focus_image.idx + "-" + i;
          let label = dets[i][5];
          boxes.push({x, y, w, h, conf, idx, label});
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
          let conf = dets[i][4];
          let label = dets[i][5];
          let idx = that.focus_text.idx + "-" + i;
          boxes.push({x, y, w, h, conf, idx, label});
        }
        this.one_image_data = {width, height, "idx": that.focus_text.idx, "x":image_x, "y": image_y};
        this.one_image_box_data = boxes;
      }
      if (this.one_image_box_data){
        this.one_image_box_data = this.one_image_box_data.filter(d =>
          d.conf > that.one_image_boxes_threshold)
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
      that.isEditing = false;
      that.main_group.selectAll("#drag-bar-g").remove();
      if(that.selectRect!==null) that.selectRect.remove();
      that.selectRect = null;
      that.selectClass = "";
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
          .attr("y", (d, i) => that.img_padding + Math.floor(i / that.x_grid_num) * (that.grid_size + that.grid_offset)-30)
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
          .attr("href", d => that.server_url + `/image/origin_image?filename=${d.idx}.jpg`)
          .on("click", (_, d) => {
              console.log("click single images");        
              that.fetch_text_by_ids([d.idx]);
          });
        // drag events
        let dragbarw = 12;
        let dragmove = function(event, d) {
          if(!that.isEditing) return;
          that.selectRect
                  .attr("x", d.x = Math.max(0, event.x))
                  .attr("y", d.y = Math.max(0, event.y))
                  .attr("width", d => d.w)
                  .attr("height", d => d.h);
          that.dragbarlefttop
                  .attr("x", d.x - (dragbarw/2))
                  .attr("y", d.y - (dragbarw/2));
          that.dragbarbottomright
                  .attr("x", d.x+d.w - (dragbarw/2))
                  .attr("y", d.y+d.h - (dragbarw/2))
        };

        let rdragresize = function(event) {
          if(!that.isEditing) return;
          let d = that.selectRect.datum();
          d.x = event.dx+d.x;
          d.y = event.dy+d.y;
          d.w = d.w-event.dx;
          d.h = d.h-event.dy;
          that.selectRect
                  .attr("x", d.x = Math.max(0, event.x))
                  .attr("y", d.y = Math.max(0, event.y))
                  .attr("width", d => d.w)
                  .attr("height", d => d.h);
          that.dragbarlefttop
                  .attr("x", d.x - (dragbarw/2))
                  .attr("y", d.y - (dragbarw/2));
        }

        let tdragresize = function(event) {
          if(!that.isEditing) return;
          let d = that.selectRect.datum();
          d.w = d.w+event.dx;
          d.h = d.h+event.dy;
          that.selectRect
                  .attr("width", d => d.w)
                  .attr("height", d => d.h);
          that.dragbarbottomright
                  .attr("x", d.x+d.w - (dragbarw/2))
                  .attr("y", d.y+d.h - (dragbarw/2))
        }

        let drag = d3.drag()
            .on("drag", dragmove);

        that.one_image_boxes.enter()
          .append("rect")
          .attr("class", "info-box")
          .attr("x", d => d.x)
          .attr("y", d => d.y)
          .attr("width", d => d.w)
          .attr("height", d => d.h)
          .style("fill", "white")
          .style("fill-opacity", "0")
          .style("stroke", Global.BoxRed)
          .style("stroke-width", 1)
          .on("click", function (event, d) {
            if(that.isEditing) return;
            that.selectRect = d3.select(this);
            that.one_image_boxes.style("stroke-width", 1);
            that.selectRect.style("stroke-width", 4);
            that.selectClass = that.$store.state.classNames[d.label];
            // add dragbar
            that.main_group.selectAll("#drag-bar-g").remove();
            let new_g = that.main_group.append("g").attr("id", "drag-bar-g");
            let draglefttop = d3.drag()
                .on("drag", rdragresize);

            let dragbottomright = d3.drag()
                .on("drag", tdragresize);

            that.dragbarlefttop = new_g.append("rect")
                  .attr("x", d.x - (dragbarw/2))
                  .attr("y", d.y - (dragbarw/2))
                  .attr("height", dragbarw)
                  .attr("id", "dragleft")
                  .attr("width", dragbarw)
                  .attr("fill", Global.BoxRed)
                  .attr("fill-opacity", 1)
                  .attr("cursor", "nw-resize")
                  .call(draglefttop);

            that.dragbarbottomright = new_g.append("rect")
                  .attr("x", d.x+d.w - (dragbarw/2))
                  .attr("y", d.y+d.h - (dragbarw/2))
                  .attr("height", dragbarw)
                  .attr("id", "dragleft")
                  .attr("width", dragbarw)
                  .attr("fill", Global.BoxRed)
                  .attr("fill-opacity", 1)
                  .attr("cursor", "nw-resize")
                  .call(dragbottomright);

            that.one_image_boxes.on('mousedown.drag', null);
            that.selectRect.call(drag);

          });
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
    show_detail(d, i) {
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
    },
    beginEditBoundingBox() {
      let that = this;
      this.isEditing = true;
      that.one_image_boxes.attr("cursor", "default");
      that.selectRect.attr("cursor", "move");
      // add context menu
      let selectNode = window.detection.selected_node.node_ids.length==0?null:window.detection.selected_node.node_ids[0];
      let menuOptions = [
                {
                    title: selectNode==null?'Confirm':'Confirm as '+ that.$store.state.classNames[selectNode],
                    action: function() {
                      console.log('Confirm!');
                      // TODO: send confirm msg


                      that.isEditing = false;
                      that.one_image_boxes.attr("cursor", "default");
                      that.main_group.selectAll("#drag-bar-g").remove();
                      that.one_image_boxes.style("stroke-width", 1);
                      that.selectRect.on('contextmenu', "none");
                      that.selectRect = null;
                    },
                }
      ];
      that.selectRect.on('contextmenu', d3ContextMenu(menuOptions));
    },
    removeBoundingBox() {
      let that = this;
      if(that.selectRect == null) return;
      that.isEditing = false;
      that.main_group.selectAll("#drag-bar-g").remove();
      // TODO: add 'deleting bounding box' code here
      // let removedBoundBox = that.selectRect.datum();


      that.selectRect.remove();
      that.selectRect = null;
      that.selectClass = "";
    }
  },
  async mounted() {
    window.image = this;
    let that = this;
    let container = d3.select(".image-content");
    // console.log("container", container);
    container.style('height', `${Global.WindowHeight * 0.405}px`);
    let bbox = container.node().getBoundingClientRect();
    that.width = bbox.width;
    that.height = bbox.height;
    that.layout_width = that.width - 20;
    that.layout_height = that.height-40;
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
      .select("#image-svg")
      .attr("width", that.width)
      .attr("height", that.layout_height - 40);

    that.svg.select("#btn-edit").attr("x", that.width-80).attr("y", 0);
    that.svg.select("#btn-remove").attr("x", that.width-50).attr("y", 0);

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
.image-legend {
  display: flex;
  justify-content: space-between;
  width: 100%;
    align-items: center;
}

.confidence-slider, .bounding-label {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.edit-legend {
  display: flex;
  justify-content: center;
}

.image-view{
  height: 34%;
}

.image-content {
  border: 0;
  border-radius: 5px;
  margin: 10px;
  /* height: calc(100% - 24px); */
  overflow-y: auto;
  overflow-x: hidden;
}

</style>