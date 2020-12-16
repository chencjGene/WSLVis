const GrayColor = "#7f7f7f";
const Animation = 100;

const deepCopy = function(obj) {
    let _obj = Array.isArray(obj) ? [] : {}
    for (let i in obj) {
      _obj[i] = typeof obj[i] === 'object' ? deepCopy(obj[i]) : obj[i]
    }
    return _obj
};

function pos2str(pos){
    return pos.y + "," + pos.x;
}

const tree_line = function(d){
    let start = {x: d.source.x, y: d.source.y};
    let middle = {x: d.target.turn_x, y: d.target.turn_y};
    let end = {x: d.target.x, y: d.target.y};
    let t1 = {x: start.x, y: (start.y + middle.y) / 2};
    let t2 = {x: middle.x, y: t1.y};
    return "M" + pos2str(start) + "C" + pos2str(t1) + "," + pos2str(t2) 
        + "," + pos2str(middle) + "L" + pos2str(end);
}

export {
    GrayColor,
    Animation,
    deepCopy,
    tree_line
}