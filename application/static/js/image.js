/*
* added by Changjian Chen, 20191015
* */

let ImageLayout = function (container){
    let that = this;
    that.container = container;
    that.GraphView = null;

    let bbox = that.container.node().getBoundingClientRect();
    let width = bbox.width;
    let height = bbox.height;
    let origin_layout_width = width - 20;
    let layout_width = width - 20;
    let layout_height = height - 40;
    let img_offset_x = 20;
    let img_offset_y = 10;
    let iter = 0;
    let img_padding = 10;
    let grid_size = 50;
    let grid_offset = 10;
    let detail_pos = -1;
    let img_width = layout_width-img_padding * 2;
    let img_height = layout_height-img_padding*2;
    let legend_height = 25;
    let AnimationDuration = 500;
    let longAnimationDuration = 500;
    let neighbor_border = 10;
    let shortAnimationDuration = 10;
    let max_height = 525;
    let image_size = layout_width;
    let get_entropy_url = "/graph/entropy";
    let x_grid_num = parseInt((layout_width-5)/(grid_offset+grid_size));

    let img_url = null;
    let img_grid_urls = [];
    let img_neighbors_ids = [];
    let show_neighbor_mode = false;
    let k_num = 6;
    let current_mode = "grid";

    let data_manager = null;

    let svg = that.container.append("svg").attr("class", "scatterplot-svg")
    .attr("width", bbox.width)
    .attr("height", bbox.height);
    let detail_group = svg.append("g").attr("id", "detail-group");
    // detail_group.append("image")
    let img_grids = svg.append("g").attr("id", "grid-group");

    that.set_data_manager = function(_data_manager) {
        data_manager = _data_manager;
    };

    that.component_update = async function(data) {
        // that.image_id = i;
        that.grid_images = data;
        that.grid_images.sort((a,b) => a.color - b.color);
        that._update_view();
        that._show_detail(null, -1);
    };

    that._update_data = async function(state) {
    
    };

    that._update_view =async function() {
        that.e_data = svg.selectAll(".one-image")
        .data([that.image_id]);
        that._create();
        that._update();
        that._remove();
    };


    that._create = function() {
        // that.e_data.enter()
        //     .append("image")
        //     .attr("class", "one-image")
        //     .attr("x", 0)
        //     .attr("y", 0)
        //     .attr("width", image_size)
        //     .attr("height", image_size)
        //     .attr("href", d => Website + ":" + Port + `/image/image?filename=${d}.jpg`);

        img_grids_g =  img_grids.selectAll(".grid-image")
            .data(that.grid_images);
        img_grids.selectAll("image").data(img_grid_urls);
        img_grids.selectAll("rect").data(img_grid_urls);
        let img_grids_enters = img_grids_g.enter()
            .append("g")
            .attr("class", "grid-image")
            .attr("transform", "translate(0,0)");

        img_grids_enters.append("image")
            .attr("xlink:href", d => Website + ":" + Port + `/image/image?filename=${d.id}.jpg`)
            .attr("x", (d, i) => img_padding+(i%x_grid_num)*(grid_size+grid_offset))
            .attr("y", (d, i) => img_padding+Math.floor(i/x_grid_num)*(grid_size+grid_offset))
            .attr("width", grid_size)
            .attr("height", grid_size)

        img_grids_enters.append("rect")
            .attr("x", (d, i) => img_padding+(i%x_grid_num)*(grid_size+grid_offset)-2)
            .attr("y", (d, i) => img_padding+Math.floor(i/x_grid_num)*(grid_size+grid_offset)-2)
            .attr("width", grid_size+4)
            .attr("height", grid_size+4)
            .attr("stroke-width", 4)
            .attr("stroke", function (d) {
                // if(use_ground_truth) return color_label[d.truth];
                // if(d.label[iter] === -1) return color_unlabel;
                //     else return color_label[d.label[iter]];
                return CategoryColor[d.color% 10];
            })
            .attr("fill-opacity", 0)
            .on("click", function(d, i){
                that._show_detail(d, i);
            })
    };

    that._update = function() {
        that.e_data
        .attr("href", d => Website + ":" + Port + `/image/image?filename=${d.id}.jpg`);
        let img_size = 250;

        img_grids_g.selectAll("rect")
            .transition()
            .duration(AnimationDuration)
            .attr("stroke", function (d) {
                // if(use_ground_truth) return color_label[d.truth];
                // if(d.label[iter] === -1) return color_unlabel;
                //     else return color_label[d.label[iter]];
                return CategoryColor[d.color % 10];
            });

        // img_grids_g.select("rect")
        //     .attr("stroke", function (d) {
        //
        //         });

        img_grids_g
            .transition()
            .duration(AnimationDuration)
            .attr("transform", (d, i) => "translate(" + 0 + ", " +
                ((detail_pos !== -1 && Math.floor(i / x_grid_num) >  Math.floor(detail_pos / x_grid_num)) * (img_padding*3+img_size)) + ")");

    };

    that._remove = function() {
        img_grids_g
            .exit()
            .remove();

    };

    that._show_detail = function (d, i) {
        if(i===-1){
            detail_pos = -1;
            detail_group.style("opacity", 0);
            detail_group.selectAll("image").remove();
            detail_group.append("image");
            showing_image = false;
            return;
        }
        showing_image = true;
        img_url = Website + ":" + Port + `/image/origin_image?filename=${d.id}.jpg`;
        console.log("show detail:", detail_pos, img_url);
        layout_width = parseFloat(svg.attr("width"));
        let img_width = x_grid_num*(grid_size+grid_offset)-grid_offset-img_padding*2;
        let img_size = 250;
        let x_padding = (layout_width-img_size)/2;
        if (detail_pos === -1) {
            detail_pos = i;
            detail_group.transition()
                .duration(AnimationDuration)
                .style("opacity", 1);
            detail_group.select("image")
                .attr("xlink:href", img_url)
                .attr("x", img_padding)
                .attr("y", img_padding+(Math.floor(i/x_grid_num)+1)*(grid_size+grid_offset))
                .attr("width", 0)
                .attr("height", 0)
                .transition()
                .duration(AnimationDuration)
                .attr("x", x_padding)
                .attr("y", img_padding+(Math.floor(i/x_grid_num)+1)*(grid_size+grid_offset))
                .attr("width", img_size)
                .attr("height", img_size);
            that._update_view();
        } else if (detail_pos === i) {
            detail_pos = -1;
            detail_group.transition()
                .duration(AnimationDuration)
                .style("opacity", 0);
            detail_group.select("image")
                .transition()
                .duration(AnimationDuration)
                .attr("x", x_padding)
                .attr("y", img_padding+(Math.floor(i/x_grid_num)+1)*(grid_size+grid_offset))
                .attr("width", 0)
                .attr("height", 0);
            that._update_view();
        } else {
            detail_pos = i;
            detail_group.transition()
                .duration(AnimationDuration)
                .style("opacity", 1);
            detail_group.select("image")
                .attr("xlink:href", img_url)
                .transition()
                .duration(AnimationDuration)
                .attr("x", x_padding)
                .attr("y", img_padding+(Math.floor(i/x_grid_num)+1)*(grid_size+grid_offset))
                .attr("width", 0)
                .attr("height", 0)
                .on("end", function () {
                    let image = d3.select(this);
                    image.remove();
                });
            detail_group.append("image")
                .attr("xlink:href", img_url)
                .attr("x", img_padding)
                .attr("y", img_padding+(Math.floor(i/x_grid_num)+1)*(grid_size+grid_offset))
                .attr("width", 0)
                .attr("height", 0)
                .transition()
                .duration(AnimationDuration)
                .attr("x", x_padding)
                .attr("y", img_padding+(Math.floor(i/x_grid_num)+1)*(grid_size+grid_offset))
                .attr("width", img_size)
                .attr("height", img_size);
            that._update_view();
        }
    };



};
