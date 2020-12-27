const GrayColor = "#7f7f7f";
const Animation = 100;

const deepCopy = function(obj) {
    let _obj = Array.isArray(obj) ? [] : {}
    for (let i in obj) {
      _obj[i] = typeof obj[i] === 'object' ? deepCopy(obj[i]) : obj[i]
    }
    return _obj
};

function pos2str_inverse(pos){
    return pos.y + "," + pos.x;
}

function pos2str(pos){
    return pos.x + "," + pos.y;
}

const tree_line = function(d){
    let start = {x: d.source.x, y: d.source.y};
    let middle = {x: d.target.turn_x, y: d.target.turn_y};
    let end = {x: d.target.x, y: d.target.y};
    let t1 = {x: start.x, y: (start.y + middle.y) / 2};
    let t2 = {x: middle.x, y: t1.y};
    return "M" + pos2str_inverse(start) + "C" + pos2str_inverse(t1) + "," + pos2str_inverse(t2) 
        + "," + pos2str_inverse(middle) + "L" + pos2str_inverse(end);
}

const set_line = function(d){
    let start = {x: d.source.x, y: d.source.y};
    let middle = {x:d.turn_point.x, y: d.turn_point.y};
    let end = {x: d.target.x, y: d.target.y};
    let t1 = {x: (middle.x + end.x) / 2, y: middle.y};
    let t2 = {x: t1.x, y: end.y};
    return "M" + pos2str(start) + "L" + pos2str(middle) + "C" 
        + pos2str(t1) + "," + pos2str(t2) + "," + pos2str(end);
}

const getTextWidth = function(text, font) {
    let canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    let context = canvas.getContext("2d");
    context.font = font;
    return context.measureText(text).width;
  }

export {
    GrayColor,
    Animation,
    deepCopy,
    tree_line,
    getTextWidth,
    set_line
}