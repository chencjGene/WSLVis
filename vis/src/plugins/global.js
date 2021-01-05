const GrayColor = "#7f7f7f";
const Animation = 1000;

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

const node_icon = function(x, y, type){
    let basic_ratio = 2;
    if (type === 0){
        let ratio = basic_ratio * 1.8;
        let p1 = {x: x + ratio, y: y};
        let p2 = {x: x - 0.5 * ratio, y: y - 0.866 * ratio};
        let p3 = {x: x - 0.5 * ratio, y: y + 0.866 * ratio};
        return "M" + pos2str(p1) + "L" + pos2str(p2) + "L" + pos2str(p3) + "Z";
    }
    else if (type === 1){
        let ratio = basic_ratio * 1.8;
        let p1 = {x: x, y: y + ratio};
        let p2 = {x: x + 0.866 * ratio, y: y - 0.5 * ratio};
        let p3 = {x: x - 0.866 * ratio, y: y - 0.5 * ratio};
        return "M" + pos2str(p1) + "L" + pos2str(p2) + "L" + pos2str(p3) + "Z";
    }
    else if (type === 2){
        let ratio = basic_ratio;
        return "M " + (x - ratio) + ", " + (y) + 
            "a" + ratio + ", " + ratio + " 0 1, 0 " + (ratio * 2) + ", 0" +  
            "a" + ratio + ", " + ratio + " 0 1, 0 " + (- ratio * 2) + ", 0"; 
    }
    else if (type === -1){
        return "M 0,0 L 0,0";
    }
    else{
        return 1;
    }
}

function plus_path_d(start_x, start_y, width, height, k) {
    let sum_k = 2 * k + 1;
    let x = [start_x, start_x + k / sum_k * width, start_x + (k + 1) / sum_k * width, start_x + width];
    let y = [start_y, start_y + k / sum_k * height, start_y + (k + 1) / sum_k * height, start_y + height];
    let d = `M${x[0]},${y[1]}`;
    d += `L${x[1]},${y[1]}`;
    d += `L${x[1]},${y[0]}`;
    d += `L${x[2]},${y[0]}`;
    d += `L${x[2]},${y[1]}`;
    d += `L${x[3]},${y[1]}`;
    d += `L${x[3]},${y[2]}`;
    d += `L${x[2]},${y[2]}`;
    d += `L${x[2]},${y[3]}`;
    d += `L${x[1]},${y[3]}`;
    d += `L${x[1]},${y[2]}`;
    d += `L${x[0]},${y[2]}`;
    d += `L${x[0]},${y[1]}`;
    return d;
}

function minus_path_d(start_x, start_y, width, height, k){
    let sum_k = 2 * k + 1;
    let x = [start_x, start_x  + width];
    let y = [start_y + k / sum_k * height, start_y + (k + 1) / sum_k * height];
    let d = `M${x[0]},${y[0]}`; 
    d += `L${x[1]},${y[0]}`
    d += `L${x[1]},${y[1]}`
    d += `L${x[0]},${y[1]}`;
    return d;
}

function half_rounded_rect(x, y, w, h, r_left, r_right){
    // assert(w > 2 * r, "w > 2 * r")
    // assert(h > r, "h > r")
    let p1 = {x: x, y: y};
    let p2 = {x: x + w, y: y};
    let p3 = {x: x + w, y: y + h - r_right};
    let delta4 = {x: -r_right, y: r_right};
    let p5 = {x: x + r_left, y: y + h};
    let delta6 = {x: -r_left, y: - r_left};
    return "M" + pos2str(p1) + "L" + pos2str(p2) + "L" + pos2str(p3) + "a" + r_right + ", " + r_right
        + " 0,0,1 " + pos2str(delta4) + "L" + pos2str(p5) +  "a" + r_left + ", " + r_left 
        + " 0,0,1 " + pos2str(delta6) + "z";
}

export {
    GrayColor,
    Animation,
    deepCopy,
    tree_line,
    getTextWidth,
    set_line,
    node_icon,
    plus_path_d,
    minus_path_d,
    half_rounded_rect
}