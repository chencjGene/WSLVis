function unique(arr){
    return Array.from(new Set(arr));
}

const SetManager = function (){
    let that = this;

    that.leaf_nodes = [];

    this.update_leaf_nodes = function(leaf_nodes){
        that.leaf_nodes = leaf_nodes;
    }

    this.get_sets = function(){
        let arr = that.leaf_nodes.map(d => d.data.sets);
        arr = Array.prototype.concat.call(...arr);
        arr = unique(arr);
        console.log("arr in get_sets", arr);
        // TODO: filtering or sorting
        return arr.slice(0, 20);
    }
}

export {SetManager}