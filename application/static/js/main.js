
let Embedding = [];
let Website = "http://localhost"
let Port = "20211"
let EmbeddingApi = "/detection/Embedding"
let CategoryColor = [
    "#777777",
    "#ff7f0e", // orange, text false pos
    "#9467bd", // violet, text false neg // 这种是要找到 bounding box的
    "#d62728", // red, image false pos // 这种是要去掉bounding box的
    "#8c564b", //brown, image false neg
    "#1f77b4",
    "#2ca02c",
    "#e377c2",
    "#ffdb45",
    "#bcbd22",
    "#17becf",];

var load_data = function (dataset) {
    /*
    * load data that need to be stored in global variables
    * */
    console.log("loading data...");
    DatasetName = dataset;
    var params = "?dataset=" + DatasetName;
    var embedding_node = new request_node(Website + ":" + Port + EmbeddingApi + params, (data)=> {
        Embedding = data;
        setup();
    }, "json", "GET");
    embedding_node.notify();
    console.log("loading finished.")
};

var remove_dom = function(){
    d3.select("#block-1-1").selectAll("svg").remove();
    d3.select("#block-1-2").selectAll("svg").remove();
    d3.select("#block-2-1").selectAll("svg").remove();
};

var setup = function () {
    EmbeddingView = new ScatterPlot(d3.select("#block-1-1"));
    EmbeddingView._update_data(Embedding);
    EmbeddingView._update_view();
    ImageView = new ImageLayout(d3.select("#block-2-1"));
};

var update_image_view = function(d, i){
    console.log("update_image_view", d, i);
    ImageView.component_update(d, i);
};

$(document).ready(function () {

    load_data("bird");
});