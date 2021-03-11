import * as Global from "../plugins/global";
import * as d3 from "d3";

const ImageCards = function(parent) {
  let that = this;
  that.parent = parent;
  that.server_url = that.parent.server_url;

  that.set_group = that.parent.set_group;
  that.grid_group = that.parent.grid_group;
  that.label_group = that.parent.label_group;

  // animation
  that.create_ani = that.parent.create_ani;
  that.update_ani = that.parent.update_ani;
  that.remove_ani = that.parent.remove_ani;

  //
  that.boundingbox_width = 3;

  // let labels = Array(); // Label layout
  let img_width = 40;

  let margin_size = 20;
  let margin_top_size = 100;
  let plot_width = 800;
  let plot_height = 800;
  var offset_x = 0; // position of the left grid when the mode is "juxtaposition"
  var offset_y = 100;

  let mouse_pressed = false;
  let mouse_pos = {
    x: -1,
    y: -1,
  };

  that.relative_sampling_area = {
    x: 0,
    y: 0,
    w: 1,
    h: 1,
  };
  let plot_x,
    plot_y = 1;
  that.click_ids = [-1];
  that.click_count = 0;
  that.labels = [];

  this.get_set_layout_from_parent = function() {
    // set
    that.layout_height = that.parent.layout_height;
    that.set_height = that.parent.set_height;
    that.set_left = that.parent.set_left;
    that.set_width = that.parent.set_width;
    that.set_margin = that.parent.set_margin;
    that.image_height = that.parent.image_height;
    that.image_margin = that.parent.image_margin;
    that.text_height = that.parent.text_height;
  };
  this.get_set_layout_from_parent();

  (this.set_focus_image = function(image) {
    that.parent.set_focus_image(image);
  }),
    (this.set_expand_set_id = function(id) {
      that.parent.set_expand_set_id(id);
    });

  this.get_expand_set_id = function() {
    return that.parent.expand_set_id;
  };

  this.get_grid_data = function() {
    return that.parent.grid_data;
  };

  this.fetch_grid_layout = function(query) {
    return that.parent.fetch_grid_layout(query);
  };

  this.sub_component_update = function(
    sets,
    vis_image_per_cluster,
    grids,
    grids_pos
  ) {
    // update layout config
    that.get_set_layout_from_parent();

    // update state
    that.vis_image_per_cluster = vis_image_per_cluster;
    that.grids = grids;
    offset_x = grids_pos.offset_x;
    offset_y = grids_pos.offset_y;
    plot_width = grids_pos.side_length;
    plot_height = grids_pos.side_length;
    Object.values(that.vis_image_per_cluster).forEach((d) => {
      let x = that.image_margin;
      d.forEach((n) => {
        n.vis_h = that.image_height;
        n.vis_w = that.image_height;
        n.x = x;
        x = x + n.vis_w + that.image_margin;
      });
    });
    that.labels = that.label_layout(Global.deepCopy(that.grids), 
        plot_width, that.labels);
    console.log("image card sub component update", sets, grids);

    // update view
    that.e_sets = that.set_group.selectAll(".set").data(sets, d => d.id);
    that.e_grids = that.grid_group
      .selectAll(".grid")
      .data(grids, d => d.img_id);
    that.e_labels = that.label_group.selectAll(".label").data(that.labels, d => d.img_id);

    that.remove();
    that.update();
    that.create();
  };

  this.create = function() {
    that.set_create();
    that.grid_create();
    that.label_create();
  };

  this.set_create = function() {
    // set
    let set_groups = that.e_sets
      .enter()
      .append("g")
      .attr("class", "set")
      .attr("id", (d) => "set-" + d.id)
      .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")");
    set_groups
      .style("opacity", 0)
      .transition()
      .duration(that.create_ani)
      .delay(that.update_ani + that.remove_ani)
      .style("opacity", 1);

    // expand icon
    set_groups
      .append("rect")
      .attr("class", "expand-rect")
      .attr("x", -11)
      .attr("y", 0)
      .attr("width", 10)
      .attr("height", 10)
      .style("rx", 3)
      .style("ry", 3)
      .style("fill", "white")
      .style("stroke", "gray")
      .style("stroke-width", 1)
      .on("click", (_, d) => {
        if (d.id === that.get_expand_set_id()) {
          that.set_expand_set_id(-1);
        } else {
          that.set_expand_set_id(d.id);
        }
      });

    set_groups
      .append("path")
      .attr("class", "expand-path")
      .style("stroke", "none")
      .style("fill", "gray")
      .attr("d", Global.plus_path_d(-11, 0, 10, 10, 2));

    set_groups
      .append("rect")
      .attr("class", "background")
      .style("fill", "white")
      .style("stroke", "#e0e0e0")
      .style("stroke-width", 1)
      .attr("width", (d) => d.width)
      .attr("height", (d) => d.height);

    that.image_groups = set_groups
      .selectAll("g.detection-result")
      .data((d) => that.vis_image_per_cluster[d.id]);
    let g_image_groups = that.image_groups
      .enter()
      .append("g")
      .attr("class", "detection-result")
      .attr(
        "transform",
        (d) => "translate(" + d.x + ", " + that.image_margin / 2 + ")"
      );

    g_image_groups
      .append("image")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", (d) => d.vis_w)
      .attr("height", (d) => d.vis_h)
      .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
      .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none")
      .attr(
        "href",
        (d) => that.server_url + `/image/image?filename=${d.idx}.jpg`
      )
      .on("click", (_, d) => {
        console.log("click image", d);
        that.set_focus_image(d);
      });

    that.box_groups = g_image_groups.selectAll("rect.box").data((d) => {
      let dets = d.d;
      let res = [];
      for (let i = 0; i < dets.length; i++) {
        let x = d.vis_w * dets[i][0];
        let width = d.vis_w * (dets[i][2] - dets[i][0]);
        let y = d.vis_h * dets[i][1];
        let height = d.vis_h * (dets[i][3] - dets[i][1]);
        res.push({ x, y, width, height });
      }
      return res;
    });
    that.box_groups
      .enter()
      .append("rect")
      .attr("class", "box")
      .attr("x", (d) => d.x)
      .attr("y", (d) => d.y)
      .attr("width", (d) => d.width)
      .attr("height", (d) => d.height)
      .style("fill", "none")
      .style("stroke", "green")
      .style("stroke-width", 1)
      .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
      .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");
  };

  this.grid_create = function() {
    let grid_groups = that.e_grids
      .enter()
      .append("g")
      .attr("class", "grid")
      .attr("id", (d) => "grid-id-" + d.img_id)
      .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")")
      .on("mouseover", function() {
        d3.select(this)
          .select("rect")
          .style("stroke-width", 2.0);
      })
      .on("mouseout", function() {
        d3.select(this)
          .select("rect")
          .style("stroke-width", 0.0);
      });
    // TOOD: mouseover, mouseout
    grid_groups
      .style("opacity", 0)
      .transition()
      .duration(that.create_ani)
      .delay(that.update_ani + that.remove_ani)
      .style("opacity", 1);

    grid_groups
      .append("rect")
      .attr("class", "boundingbox")
      .attr("x", 0)
      .attr("y", 0)
      .attr("width", (d) => d.width)
      .attr("height", (d) => d.width)
      .style("fill", (d) => (d.mismatch > 0 ? Global.Orange : Global.GrayColor))
      .style("stroke", "black")
      .style("stroke-width", 0)
      .style("stroke-opacity", 1);

    grid_groups
      .append("rect")
      .attr("class", "display")
      .attr("x", 0.5 * that.boundingbox_width)
      .attr("y", 0.5 * that.boundingbox_width)
      .attr("width", (d) => d.width - that.boundingbox_width)
      .attr("height", (d) => d.width - that.boundingbox_width)
      .style("fill", (d) => (d.mismatch > 0 ? Global.Orange : Global.GrayColor))
      .style("pointer-events", "none");
  };

  this.label_create = function(){
    let label_group = that.e_labels
        .enter()
        .append("g")
        .attr("class", "label")
        .attr("id", d => "label-id-" + d.img_id);
    label_group
        .style("opacity", 0)
        .transition()
        .duration(that.create_ani)
        .delay(that.update_ani + that.remove_ani)
        .style("opacity", 1);
    label_group
        .append("rect")
        .attr("x", d => d.grid.x + offset_x)
        .attr("y", d => d.grid.y + offset_y)
        .attr("width", d => d.grid.w)
        .attr("height", d => d.grid.h)
        .style("fill", "none")
        .style("stroke", "grey")
        .style("stroke-width", 2);
    label_group
        .append("image")
        .attr("x", d => d.label.x + offset_x)
        .attr("y", d => d.label.y + offset_y)
        .attr("width", d => d.label.w)
        .attr("height", d => d.label.h)
        .attr("xlink:href", d => that.server_url + `/image/image?filename=${d.img_id}.jpg`);
  }

  this.update = function() {
    that.set_update();
    that.grid_update();
    that.label_update();
  };

  this.set_update = function() {
    that.e_sets
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")");

    that.e_sets
      .select("rect.background")
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      .attr("height", (d) => d.height);

    that.e_sets
      .selectAll("g.detection-result")
      .select("image")
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      // .attr("height", d => that.get_expand_set_id() === -1 ? d.vis_h : 0);
      .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
      .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");

    that.e_sets
      .selectAll("g.detection-result")
      .selectAll("rect.box")
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      .style("opacity", that.get_expand_set_id() === -1 ? 1 : 0)
      .style("pointer-events", that.get_expand_set_id() === -1 ? 1 : "none");

    that.e_sets
      .select(".expand-path")
      .attr("d", (d) =>
        d.id === that.get_expand_set_id()
          ? Global.minus_path_d(-11, 0, 10, 10, 2)
          : Global.plus_path_d(-11, 0, 10, 10, 2)
      );
  };

  this.grid_update = function() {
    that.e_grids
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      .attr("transform", (d) => "translate(" + d.x + ", " + d.y + ")");

    that.e_grids
      .select(".boundingbox")
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      .attr("width", (d) => d.width)
      .attr("height", (d) => d.width)
      .style("fill", (d) =>
        d.mismatch > 0 ? Global.Orange : Global.GrayColor
      );

    that.e_grids
      .select(".display")
      .transition()
      .duration(that.update_ani)
      .delay(that.remove_ani)
      .attr("width", (d) => d.width - that.boundingbox_width)
      .attr("height", (d) => d.width - that.boundingbox_width)
      .style("fill", (d) =>
        d.mismatch > 0 ? Global.Orange : Global.GrayColor
      );
  };

  this.label_update = function(){

  }

  this.remove = function() {
    that.set_remove();
    that.grid_remove();
    that.label_remove();
  };

  this.set_remove = function() {
    that.e_sets
      .exit()
      .transition()
      .duration(that.remove_ani)
      .style("opacity", 0)
      .remove();
  };

  that.grid_remove = function() {
    that.e_grids
      .exit()
      .transition()
      .duration(that.remove_ani)
      .style("opacity", 0)
      .remove();
  };

  this.label_remove = function(){

  }

  that.set_mode = function(mode) {
    console.log("set mode", mode);
    that.mode = mode;
    if (mode === "cropping") {
      d3.select("#cropping")
        .select("path")
        .attr("d", Global.d_rollback);
      d3.select("#selecting")
        .select("path")
        .attr("d", Global.d_select);
      that.enter_overview();
    } else if (mode === "selecting") {
      d3.select("#selecting")
        .select("path")
        .attr("d", Global.d_rollback);
      d3.select("#cropping")
        .select("path")
        .attr("d", Global.d_scan);
      that.enter_overview();
    } else if (mode === "exploring") {
      d3.select("#cropping")
        .select("path")
        .attr("d", Global.d_scan);
      d3.select("#selecting")
        .select("path")
        .attr("d", Global.d_select);
      that.quit_overview();
    }
  };

  that.get_mode = function() {
    return that.mode;
  };

  that.enter_overview = function() {
    that.overview_group
      .select("#overview-1")
      .attr("x", offset_x)
      .attr("y", offset_y)
      .attr("width", plot_width)
      .attr("height", plot_height);
    // that.overview_group.select("#overview-2")
    //     .attr("x", small_x_2)
    //     .attr("y", small_y_2)
    //     .attr("width", small_grid_width)
    //     .attr("height", small_grid_width);
    that.overview_group.style("visibility", "visible");
    that.overview_group.select("#viewbox").style("visibility", "hidden");
    that.confirm_button.style("visibility", "hidden");
  };

  that.quit_overview = function() {
    that.overview_group.style("visibility", "hidden");
    that.overview_group.select("#viewbox").style("visibility", "hidden");
    that.confirm_button
      .select("#confirm-resample")
      .style("visibility", "hidden");
  };

  that._init = function() {
    that.overview_group = that.parent.svg
      .append("g")
      .attr("id", "overview-group");

    that.overview_group
      .attr("transform", "translate(" + 0 + "," + that.text_height + ")")
      .style("visibility", "hidden");
    that.overview_group
      .append("rect")
      .attr("id", "overview-1")
      .attr("class", "overview-box");
    // that.overview_group.append("rect")
    //     .attr("id", "overview-2")
    //     .attr("class", "overview-box");
    that.overview_group
      .selectAll(".overview-box")
      .attr("x", 0)
      .attr("y", 0)
      .style("fill", "white")
      .style("stroke", "grey")
      .style("stroke-width", 5)
      .style("opacity", 0.3);
    that.overview_group
      .append("rect")
      .attr("id", "viewbox")
      .style("stroke-dasharray", "5, 5")
      .style("fill", "white")
      .style("stroke", "grey")
      .style("stroke-width", 5)
      .style("opacity", 0.5);

    d3.select("#cropping").on("click", function() {
      var mode =
        d3
          .select(this)
          .select("path")
          .attr("d") === Global.d_scan
          ? "cropping"
          : "exploring";
      that.set_mode(mode);
    });

    d3.select("#selecting").on("click", function() {
      var mode =
        d3
          .select(this)
          .select("path")
          .attr("d") === Global.d_select
          ? "selecting"
          : "exploring";
      that.set_mode(mode);
    });

    function adjust_sampling_area(area) {
      that.relative_sampling_area = area;
      // console.log("relative_sampling are", that.relative_sampling_area);
      that.overview_group
        .select("#viewbox")
        .attr("x", that.relative_sampling_area.x * plot_width + offset_x)
        .attr("y", that.relative_sampling_area.y * plot_height + offset_y) //- that.text_height)
        .attr("width", that.relative_sampling_area.w * plot_width)
        .attr("height", that.relative_sampling_area.h * plot_height);
    }
    function compute_viewbox(x1, y1, x2, y2) {
      var min_x = Math.min(x1, x2),
        max_x = Math.max(x1, x2),
        min_y = Math.min(y1, y2),
        max_y = Math.max(y1, y2);
      var new_area = {
        x: (min_x - plot_x) / plot_width,
        y: (min_y - plot_y) / plot_height,
        w: (max_x - min_x) / plot_width,
        h: (max_y - min_y) / plot_height,
      };
      if (new_area.x + new_area.w > 1 && new_area.x < 1) {
        return that.relative_sampling_area;
      } else {
        return new_area;
      }
    }

    that.overview_group
      .on("mousedown", function(ev) {
        // var offset = $(d3.select(this).node()).offset();
        plot_x = offset_x;
        plot_y = offset_y + that.text_height;
        mouse_pos = {
          x: ev.offsetX,
          y: ev.offsetY,
        };
        console.log(plot_x, plot_y, mouse_pos);
        mouse_pressed = d3.select(this).attr("id");
        that.overview_group.select("#viewbox").style("visibility", "visible");
        that.confirm_button.style("visibility", "hidden");
        adjust_sampling_area(
          compute_viewbox(mouse_pos.x, mouse_pos.y, mouse_pos.x, mouse_pos.y)
        );
      })
      .on("mousemove", function(ev) {
        if (!mouse_pressed) {
          return;
        }

        adjust_sampling_area(
          compute_viewbox(mouse_pos.x, mouse_pos.y, ev.offsetX, ev.offsetY)
        );

        let left_x = that.relative_sampling_area.x;
        let top_y = that.relative_sampling_area.y;
        let right_x = left_x + that.relative_sampling_area.w;
        let bottom_y = top_y + that.relative_sampling_area.h;
        // console.log("relative sampling area", left_x, right_x, top_y, bottom_y);
        if (that.get_mode() !== "exploring") {
          let grid_data = that.get_grid_data();
          grid_data.forEach((d) => {
            let x = d.pos[0];
            let y = d.pos[1];
            let width = d.normed_w;
            if (
              x + width > left_x &&
              x < right_x &&
              y + width > top_y &&
              y < bottom_y
            ) {
              if (d.selected === false) {
                d.selected = true;
                d3.select("#grid-id-" + d.img_id)
                  .select(".boundingbox")
                  .style(
                    "fill",
                    d.mismatch > 0
                      ? d3.rgb(Global.Orange).darker(1.5)
                      : d3.rgb(Global.GrayColor).darker(1.5)
                  );
                d3.select("#grid-id-" + d.img_id)
                  .select(".display")
                  .style(
                    "fill",
                    d.mismatch > 0
                      ? d3.rgb(Global.Orange).darker(1.5)
                      : d3.rgb(Global.GrayColor).darker(1.5)
                  );
              }
            } else {
              if (d.selected === true) {
                d.selected = false;
                d3.select("#grid-id-" + d.img_id)
                  .select(".boundingbox")
                  .style(
                    "fill",
                    d.mismatch > 0 ? Global.Orange : Global.GrayColor
                  );
                d3.select("#grid-id-" + d.img_id)
                  .select(".display")
                  .style(
                    "fill",
                    d.mismatch > 0 ? Global.Orange : Global.GrayColor
                  );
              }
            }
          });
        }
      })
      .on("mouseup", function(ev) {
        if (!mouse_pressed) {
          return;
        }
        mouse_pressed = false;
        adjust_sampling_area(
          compute_viewbox(mouse_pos.x, mouse_pos.y, ev.offsetX, ev.offsetY)
        );
        let button_x =
          (that.relative_sampling_area.x + that.relative_sampling_area.w) *
            plot_width +
          margin_size +
          offset_x;
        let button_y =
          (that.relative_sampling_area.y + that.relative_sampling_area.h) *
            plot_height +
          margin_top_size +
          offset_y;
        that.confirm_button
          .attr("transform", "translate(" + button_x + ", " + button_y + ")")
          .style("visibility", "visible");
      });

    that.confirm_button = that.parent.svg
      .append("g")
      .attr("id", "confirm-resample")
      .style("visibility", "hidden");
    that.confirm_button
      .append("circle")
      .attr("r", 20)
      .attr("fill", "grey");
    that.confirm_button
      .append("text")
      .attr("class", "glyphicon")
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .attr("dy", "0.25em")
      .style("fill", "white")
      .style("opacity", 1)
      .style("font-size", "20px")
      .style("cursor", "hand")
      .text("\ue015");

    that.confirm_button.on("click", function(ev) {
      console.log("confirm buttom click");
      if (that.get_mode() === "cropping") {
        that.click_count += 1;
        that.click_ids.push(that.click_count);
        let query = {
          "left-x": that.relative_sampling_area.x,
          "top-y": that.relative_sampling_area.y,
          width: that.relative_sampling_area.w,
          height: that.relative_sampling_area.h,
          "node-id": that.click_count,
          image_cluster_id: that.get_expand_set_id,
        };
        that.fetch_grid_layout(query);
      } else if (that.get_mode() === "selecting") {
        // let selected_items_id = [];
        // for (let i = 0; i < train_data.length; i++) {
        //     if (train_data[i].selected === true) {
        //         selected_items_id.push(train_data[i].get_id());
        //     }
        // }
        // for (let i = 0; i < test_data.length; i++) {
        //     if (test_data[i].selected === true) {
        //         selected_items_id.push(test_data[i].get_id());
        //     }
        // }
      }
      that.set_mode("exploring");
      d3.select(this).style("visibility", "hidden");
      ev.stopPropagation();
    });
  }.call();

  that.label_layout = function(data, plot_size, labels) {
    let padding_label = 40;
    if (data.length <= 25 ** 2) {
      labels = Array();
      return [];
    }
    var grid_N = Math.ceil(Math.sqrt(data.length));
    var grid_size = plot_size / grid_N;
    var img_size = img_width;
    var new_labels = [];

    var intersect = function(rect1, rect2) {
      return !(
        rect1.x + rect1.w + padding_label < rect2.x ||
        rect2.x + rect2.w + padding_label < rect1.x ||
        rect1.y + rect1.h + padding_label < rect2.y ||
        rect2.y + rect2.h + padding_label < rect1.y
      );
    };
    var legal = function(rect) {
      return (
        rect.x > 0 &&
        rect.y > 0 &&
        rect.x + rect.w < plot_size &&
        rect.y + rect.h < plot_size
      );
    };
    const offset = [
      { x: 0, y: 0 },
      { x: 0, y: -img_size },
      { x: -img_size, y: -img_size },
      { x: -img_size, y: 0 },
    ];
    data.sort((x, y) => y.mismatch - x.mismatch);
    for (let d of data) {
      var center = {
        x: d.pos[0] * plot_size + 0.5 * grid_size,
        y: d.pos[1] * plot_size + 0.5 * grid_size,
      };
      var tmp_grid = {
        x: d.pos[0] * plot_size,
        y: d.pos[1] * plot_size,
        w: d.normed_w * plot_size,
        h: d.normed_w * plot_size,
      };
      var tmp_label;
      var can_placed;
      var prev_label = labels.filter((lbl) => lbl.id === d.id);
      if (prev_label.length > 0) {
        var direction = prev_label[0].label.dir;
        tmp_label = {
          dir: direction,
          x: center.x + offset[direction].x,
          y: center.y + offset[direction].y,
          w: img_size,
          h: img_size,
        };
        can_placed = true;
        for (let r of new_labels) {
          if (
            intersect(tmp_label, r.label) ||
            intersect(tmp_grid, r.label) ||
            intersect(tmp_label, r.grid) ||
            intersect(tmp_grid, r.grid) ||
            !legal(tmp_label)
          ) {
            can_placed = false;
            break;
          }
        }
        if (can_placed) {
          new_labels.push({
            label: tmp_label,
            grid: tmp_grid,
            ...d,
          });
        }
      } else {
        for (var i = 0; i < 4; ++i) {
          tmp_label = {
            dir: i,
            x: center.x + offset[i].x,
            y: center.y + offset[i].y,
            w: img_size,
            h: img_size,
          };
          can_placed = true;
          for (let r of new_labels) {
            if (
              intersect(tmp_label, r.label) ||
              intersect(tmp_grid, r.label) ||
              intersect(tmp_label, r.grid) ||
              intersect(tmp_grid, r.grid) ||
              !legal(tmp_label)
            ) {
              can_placed = false;
              break;
            }
          }
          if (can_placed) {
            new_labels.push({
              label: tmp_label,
              grid: tmp_grid,
              ...d,
            });
            break;
          }
        }
      }
    }
    return new_labels;
  };
};

export default ImageCards;
