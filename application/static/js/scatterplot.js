/*
* added by Changjian Chen, 20191015
* */

let ScatterPlot = function (container){
    let that = this;
    that.container = container;
    that.GraphView = null;

    let bbox = that.container.node().getBoundingClientRect();
    let width = bbox.width;
    let height = bbox.height;
    let layout_width = width - 20;
    let layout_height = height - 40;
    let img_offset_x = 20;
    let img_offset_y = 10;
    let iter = 0;
    let img_padding = 10;
    let grid_size = 50;
    let grid_offset = 10;
    that.data = [];

    let colorScale = d3.scaleSequential(d3["interpolate" + "Greens"])
    .domain([0, 10])

    let img_url = null;
    let img_grid_urls = [];
    let img_neighbors_ids = [];
    let show_neighbor_mode = false;
    let k_num = 6;
    let current_mode = "grid";

    let data_manager = null;

    let svg = that.container.append("svg").attr("class", "scatterplot-svg")
        .attr("width", bbox.width)
        .attr("height", bbox.height)
    let lasso = d3.lasso()
            .closePathSelect(true)
            .closePathDistance(100);
    // let points_g = svg.append("g").attr("id", "points-group");


    that._init = function(){

    };

    that.component_update = async function(state) {
        
    };

    that._update_data = async function(state) {
        that.data = state;
        that.data.sort((a,b) => a.c - b.c)
        that.data.forEach(d => {
            d.x = d.p[0] / 1000.0 * layout_width;
            d.y = d.p[1] / 1000.0 * layout_height;
            d.color = d.c;
        })
    };

    that._update_view =async function() {
        that.e_data = svg.selectAll(".point")
        .data(that.data);

        that._create();
        that._update();
        that._remove();
        that.set_lasso();
    };


    that._create = function() {
        that.e_data.enter()
            .append("circle")
            .attr("class", "point")
            .attr("id", d => "id-" + d.id)
            .attr("r", 3)
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .style("fill", d => CategoryColor[d.color % 10]);
            // .style("fill", d => colorScale(d.color));
    };

    that._update = function() {

    };

    that._remove = function() {

    };

    that.setIter = function(newiter){

    };
    that.set_lasso = function() {
        svg.select(".lasso").remove();
        that.item_nodes = svg.selectAll(".point").data(that.data);
        lasso.items(that.item_nodes)
            .targetArea(svg)
            .on("start", that.lasso_start)
            .on("draw", that.lasso_draw)
            .on("end", that.lasso_end);
        svg.call(lasso);
    };

    that.remove_lasso = function() {
        svg.select(".lasso").remove();
    };

    that.lasso_start = function () {
        lasso_select_path = [];
        lasso.items()
            .attr("r", 3) // reset size
            .classed("not_possible", true)
            .classed("selected", false);
    };

    that.lasso_draw = function () {
        // let path_node = d3.mouse(view.main_group.node());
        // lasso_select_path.push({x:path_node[0], y:path_node[1]});
        // Style the possible dots
        lasso.possibleItems()
            .classed("not_possible", false)
            .classed("possible", true)
            .attr("r", 5);
        //
        // // Style the not possible dot
        lasso.notPossibleItems()
            .classed("not_possible", true)
            .classed("possible", false)
            .attr("r", 3);

    };

    that.lasso_end =async function () {
        that.selected_data = lasso.selectedItems().data();
        console.log("selected_data", that.selected_data);
        ImageView.component_update(that.selected_data);

    };

 
    that.init = function(){
        that._init();
    }.call();

};
