import * as d3 from "d3"
// import {deepCopy} from "../plugins/global"

function assert(flag, string){
    if (!flag){
      throw Error(string);
    }
}

// function expand_tree(tree, original_tree){
//     let node_num = tree.descendants().length;
//     for (let i = 0; i < node_num; i++){
//         original_tree.descendants()[i].shadow = tree.descendants()[i];
//     }
//     let max_depth = Math.max.apply(null, tree.descendants().map(d => d.depth));
//     console.log("max_depth", max_depth);
//     tree.descendants().forEach(d =>{
//         if (!d.children) d.children = [];
//         if (d.children && d.children.length === 0){
//             // d.children = undefined;
//             let current_node = d;
//             for (let i = d.depth; i < max_depth; i++){
//                 current_node.children = [];
//                 let new_node = current_node.copy();
//                 new_node.packing = true;
//                 new_node.depth = current_node.depth + 1;
//                 new_node.parent = current_node;
//                 new_node.id = current_node.id;
//                 new_node.name = current_node.name;
//                 current_node.children.push(new_node);
//                 // console.log("current_node", current_node, new_node);
//                 current_node = new_node;
//             }
//             current_node.children = undefined;
//         }
//     });
// }

// function shrink_tree(tree, original_tree){
//     console.log("shrink tree");
//     original_tree.descendants().forEach(_d => {
//         let d = _d.shadow;
//         if (!d.packing && d.children && d.children.length == 1 && d.children[0].packing){
//             console.log("shrink tree", _d.id, _d.name, d.x, d.y, d.depth);
//             let last_node = d.children[0];
//             while(last_node.children && last_node.children.length === 1){
//                 last_node = last_node.children[0];
//             }  
//             console.log("last_node", last_node.x, last_node.y, last_node.depth);
//             assert((!last_node.children || last_node.children.length === 0), "last node error");
//             _d.turn_x = d.x;
//             _d.turn_y = d.y;

//             // trees with turning points
//             // _d.x = last_node.x;
//             // _d.y = last_node.y;
            
//             // trees without turning points
//             _d.x = d.x;
//             _d.y = d.y;
//         }
//         else{
//             _d.turn_x = d.x;
//             _d.turn_y = d.y;
//             _d.x = d.x;
//             _d.y = d.y
//         }
//     });
// }

// const tree_layout = function (nodeSize, separation){
//     // d3.tree cannot accept a tree with leaves whose children is []
//         // wrapping d3.tree into a function that can accept such trees
//     let _this = this;
//     _this._layout = d3.tree()
//     .nodeSize(nodeSize)
//     .separation(separation);

//     this.layout = function(data){
//         let fake_tree = data.copy();
//         // TODO: stress each leaf node to max depth
//         expand_tree(fake_tree, data);
//         console.log("expand_tree", fake_tree);
        
//         fake_tree = _this._layout(fake_tree);
        
//         // TODO: recover original tree
//         shrink_tree(fake_tree, data);

//         return data;
//     }
// }

const mini_tree_layout = function(Size){
    let that = this;
    that.Size = Size;
    
    this.layout = function(data){
        // backup state
        data.all_descendants.forEach(d => {
            d.backup_children = d.children;
            d.children = d.all_children;
            if (d.children && d.children.length === 0) d.children = undefined;
            d.backup_x = d.x;
            d.backup_y = d.y;
        });

        // tree layout
        data = d3.tree()
        .size(that.Size)(data);
        
        let nodes = data.descendants();
        let links = data.links();

        // restore state 
        data.descendants().forEach(d => {
            d.mini_x = d.x;
            d.mini_y = d.y;
            d.x = d.backup_x;
            d.y = d.backup_y;
            d.children = d.backup_children;
            d.mini_selected = false;
        });

        // set selected state
        data.descendants().forEach(d => d.mini_selected = true);

        return {nodes, links};
    };
};

const tree_layout = function(nodeSize){
    let that = this;
    that.x_delta = nodeSize[0];
    that.y_delta = nodeSize[1];

    this.layout = function(data, expand_tree){
        if (expand_tree === false){
            return that._aligned_layout(data);
        }
        else{
            return that._layout(data);
        }
    };

    this.layout_with_nodes = function(data, expand_tree){
        if (expand_tree === false){
            return that._aligned_layout(data);
        }
        else{
            const root = that._layout(data);
            return root.descendants().filter(d => d.name !== "root");
        }
    };

    this._aligned_layout = function(data){
        data.descendants().forEach(d => {
            if (!d.children) d.children = [];
        });
        let nodes = data.descendants().filter(d => d.children.length === 0);
        let y_delta = that.y_delta * (data.descendants().length - 1) / nodes.length;
        let layer = 0;
        data.eachBefore(d => {
            if (d.children.length === 0){
                d.y = layer * y_delta;
                layer += 1;
            }
        })
        nodes.forEach((d) => {
            d.x = 0;
            d.link_x = 0;
            d.link_top = that.y_delta / 2;
            d.link_bottom = d.link_top;
        });
        return nodes;
    }

    this._layout = function(data){
        data.eachBefore((d,i) => {
            d.x = (d.depth - 1) * that.x_delta;
            d.y = (i - 1) * that.y_delta;
        });
        data.descendants().forEach(d => {
            if (!d.children) d.children = [];
        })
        // calculate node link 
        data.descendants().forEach(d => {
            d.link_x = 0;
            d.link_top = that.y_delta / 2;
            if (d.children && d.children.length > 0){
                d.link_bottom = d.link_top + (d.descendants().length - 1) * that.y_delta;
            }
            else{
                d.link_bottom = d.link_top;
            }
        })
        // calculate node type
        data.descendants().forEach(d => {
            let type = -1;
            if (!d.all_children || d.all_children.length===0){
                type = 2;
            }
            else{
                if (!d.children || d.children.length===0){
                    type = 0;
                }
                else{
                    type = 1;
                }
            }
            d.type = type;
        });
        return data;
    }

}

const TreeCut = function (bbox_width, bbox_height) {
    let _this = this;
    let _tree = null;
    let _tree_layout = null;
    let _bbox_width = bbox_width;
    let _bbox_height = bbox_height;
    let pinArray = [];
    let clickQueue = [];
    let tmp_children = {};
    clickQueue.insertAt = function (index, obj) {
        this.splice(index, 0, obj);
    };
    clickQueue.removeAt = function (index) {
        this.splice(index, 1);
    };

    this._update_tree = function(tree){
        _tree = tree;
        return true;
    };

    this._update_tree_layout = function(tree_layout){
        _tree_layout = tree_layout;
        return true;
    };

    this.candraw = function(root){
        let nodes = _tree_layout(root).descendants();
        _this.recover_children(root);
        let x1 = Number.MAX_VALUE, x2 = Number.MIN_VALUE, y1 = Number.MAX_VALUE, y2 = Number.MIN_VALUE;
        for (let i = 0; i < nodes.length; i++) {
            let node = nodes[i];
            if ((node.x - node._total_width/2) < x1) {
                x1 = node.x - node._total_width/2;
            }
            if ((node.x + node._total_width/2) > x2) {
                x2 = node.x + node._total_width/2;
            }
            if (node.y < y1) {
                y1 = node.y;
            }
            if (node.y > y2) {
                y2 = node.y;
            }
        }
        //if(max_depth === 5){
        //    console.log("candraw max_depth", max_depth, y2, y1);
        //}
        // console.log(x1, x2, y1, y2, bbox_width, bbox_height);
        if (x2 - x1 > _bbox_width - 20 || y2 - y1 > _bbox_height) {
            return false;
        }
        //if(max_depth === 5){
        //    console.log("candraw max_depth", max_depth);
        //}
        let offset = (x1 + x2) / 2 + 10;
        // console.log("offset:", offset);
        if (!offset){
            offset = 0.001;
        }
        return offset;
    };

    this.recover_children = function(source){
        let that = this;
        if(!source.children) source.children=[];
        source.all_children.forEach(d => that.recover_children(d));
    };

    this.initial = function(root){
        _this._initial(root);
    };

    this._initial = function (d) {
        // if (!d._children) {
        //     d._children = [];
        // }
        if (!d.children) {
            d.children = [];
        }
        if (!d.all_children){
            d.all_children = [];
        }
        if (!d.window) {
            d.window = {};
        }
        if (!d.window.x) {
            d.window.x = 0;
        }
        if (!d.window.y) {
            d.window.y = 0;
        }
        if (!d.beforeList) {
            d.beforeList = [];
        }
        if (!d.afterList) {
            d.afterList = [];
        }
        // let ratio = d.value_new.reduce((acc,x) => acc + x) / d.value.reduce((acc,x) => acc + x);
        //d.api = d._total_width * (1 + 10 * ratio) - 5 * Uncertainty(d);
        d.api = 1 //Math.sqrt(d._total_width) * (1 + 10 * ratio) ;
        assert(!isNaN(d.api), "api NaN error");
        d.doi = d.api;
        d.all_children.forEach(_this._initial);
    };

    this.drawPin = function () {
        for (let i = 0; i < pinArray.length; i++) {
            _this.draw_single_node(pinArray[i]);
        }
    };

    this.update_before_after_cnt_field = function (source) {
        // update before list and after list according window.x and window.y
        source.beforeList = [];
        for (let i = source.window.x - 1; i >= 0; i--) {
            if (source.children.indexOf(source.all_children[i]) < 0) {
                source.beforeList.push(source.all_children[i]);
            }
        }
        source.afterList = [];
        for (let i = source.window.y; i < source.all_children.length; i++) {
            if (source.children.indexOf(source.all_children[i]) < 0) {
                source.afterList.push(source.all_children[i]);
            }
        }
    };

    this.update_has_after_cnt_field = function (source) {
        // initial before list and update after list
        source.beforeList = [];
        source.afterList = [];
        if (source.children.length === 0){
            return;
        }

        for (let i = 0; i < source.all_children.length; i++) {
            if (source.children.indexOf(source.all_children[i]) < 0) {
                source.afterList.push(source.all_children[i]);
            }
        }
    };

    this.check_order = function(arr){
        if (arr.length < 2) return;
        for(let i = 0; i < arr.length-1; i++){
            // assert(arr[i].order_in_siblings <= arr[i+1].order_in_siblings, "check order error");
        }
    };

    this.from_rest_to_children = function (node) {
        // put node to children
        if (node.parent.all_children.indexOf(node) < 0) {
            return false;
        }
        if (node.parent.children.indexOf(node) < 0) {
            let parent_id = node.parent.id;
            assert(parent_id !== undefined, "parent id error");
            tmp_children[parent_id] = node.parent.children.slice(); // shallow copy

            // // added in random
            // node.parent.children.push(node);

            // added in order
            let i = 0;
            for(; i < node.parent.children.length; i++){
                if (node.parent.children[i].order_in_siblings > node.order_in_siblings){
                    break;
                }
            }
            node.parent.children.splice(i,0,node);
            this.check_order(node.parent.children);


            // reordering(node.parent);

            this.update_has_after_cnt_field(node.parent);
            return true;
        } else {
            // assert(0, "from rest to children error");
            return false;
        }
    };

    this.from_children_to_rest = function (node) {
        let id = node.parent.children.indexOf(node);
        if (id >= 0){
            // node.parent.children.splice(id, 1);
            let parent_id = node.parent.id;
            assert(tmp_children[parent_id].length === node.parent.children.length - 1, "children length error");
            node.parent.children = tmp_children[parent_id];
            _this.update_has_after_cnt_field(node.parent);
            return true;
        }
        else{
            assert(0, "from children to rest error");
            return false;
        }
    };

    this.draw_single_node = function (source) {
        //
        let node = source;
        let drawArr = [];
        while (node != null) {
            if (node.parent != null && _this.from_rest_to_children(node)) {
                drawArr.push(node);
                node = node.parent;
            } else {
                break;
            }
        }
        if (_this.candraw(_tree)) {
            return true;
        } else {
            for (let i = 0; i < drawArr.length; i++) {
                _this.from_children_to_rest(drawArr[i]);

            }
            return false;
        }
    };

    this.searchUpY = function(source){
        for (let y = source.window.y; y < source.all_children.length; y++) {
            if (source.children.indexOf(source.all_children[y]) < 0) {
                let node = source.all_children[y];
                _this.from_rest_to_children(node);
                if (!_this.candraw(_tree)) {
                    _this.from_children_to_rest(node);
                    break;
                }
            }
            source.window.y = y + 1;
        }
    };

    this.draw_my_children = function(source){
        source.window.x = 0;
        source.window.y = 0;
        _this.searchUpY(source);
    };

    this.draw_node_as_much_as_possible = function(source){
        let node = source;
        if (node != null) {
            node = node.parent;
        }
        while (node != null) {
            _this.draw_my_children(node);
            node = node.parent;
        }
    };

    this.draw_nodes_according_to_click_queue = function () {
        // try to draw as many nodes in click queue as possible
        let nodes_in_click_queue_drawn = [];
        for (let i = 0; i < clickQueue.length; i++) {
            if (_this.draw_single_node(clickQueue[i].node)){
                nodes_in_click_queue_drawn.push(clickQueue[i]);
            }
        }
        // if all nodes in click queue cannot be drawn
        if (nodes_in_click_queue_drawn.length === 0){
            _this.draw_my_children(_tree);
        }
        // try to draw the children of nodes that have been drawn
        else{
            for(let i = 0; i < nodes_in_click_queue_drawn.length; i++){
                if(nodes_in_click_queue_drawn[i].drawChildren){
                    _this.draw_my_children(nodes_in_click_queue_drawn[i].node);
                }
                _this.draw_node_as_much_as_possible(nodes_in_click_queue_drawn[i].node);
            }
        }
    };

    // this.update_rest_node = function(source){
    //     if (source.id.length > 5 && source.id.slice(0,5) === "rest-") return;
    //     if (source.beforeList.length > 0){
    //         // create a rest node
    //         let rest_node = new TreeNode();
    //         rest_node.id = "rest-before-node-" + source.id;
    //         rest_node._widthes = new Array(20).fill(0); // TODO:  20
    //         // insert the rest node in the front of children list
    //         source.children = [rest_node].concat(source.children);
    //     }
    //     if (source.afterList.length > 0){
    //         // create a rest node
    //         let rest_node = new TreeNode();
    //         rest_node.id = "rest-after-node-" + source.id;
    //         rest_node._widthes = new Array(20).fill(0); // TODO:  20
    //         // insert the rest node in the back of children list
    //         source.children.push(rest_node);
    //     }
    //     source.children.forEach(_this.update_rest_node);
    // };

    
    
    this.treeCut = function (sources, tree, tree_layout) {
        console.log("bbox width and height", bbox_width, bbox_height);
        _this._update_tree(tree);
        _this._update_tree_layout(tree_layout);
        if(!sources){
            sources = [_tree];
        }
        let source = sources[0];
        _this.initial(_tree);
        let nodes = _tree_layout(_tree).descendants(); // update depth
        nodes.forEach(d=>d.debug_visited=false);
        traverse_for_doi(_tree, source);
        clickQueue = get_selection_array(_tree, sources);
        console.log("clickqueue", clickQueue);
        pinArray = nodes.filter(d=>d.pinned);
        console.log("pinArray: ", pinArray);
        collapse(_tree);
        _this.drawPin();
        _this.draw_nodes_according_to_click_queue();
          
        // update__children(_tree);
        let offset = _this.candraw(_tree);
        assert(offset, "offset error");
        return offset;
    };

    function tree_distance(r1, r2){
        let LCA2 = function(a,b){
            while (a.depth > b.depth) {
                a = a.parent;
            }
            while (b.depth > a.depth) {
                b = b.parent;
            }
            while (a.id !== b.id) {
                a = a.parent;
                b = b.parent;
            }
            return a;
        };
        let p = LCA2(r1, r2);
        let d = r1.depth + r2.depth - p.depth * 2;
        assert(d>=0, "distance error!!!");
        if (p == r2) return d / 5;
        return d;
    }

    function traverse_for_doi(r, source) {
        assert(source, "source is empty");
        //calculate present doi
        let alpha = 0.6, beta = 0.4, decay = 0.9;
        let dis = tree_distance(r, source);
        r.doi = r.doi * (decay * alpha + 1.0 / (dis + 1) / (dis + 1) * beta);
        assert(!isNaN(r.doi), "doi NaN error!");
        r.in_selection_array = false;
        if(!r.children){return;}
        for(let i = 0; i < r.children.length; i++){
            traverse_for_doi(r.children[i], source);
        }
    }

    function get_selection_array(root, sources) {
        let selection_array = [];
        // add selected node and his children to selection array
        let source = sources[0];
        // selection_array.push({
        //     "node": source,
        //     "drawChildren": true
        // });
        sources.forEach(d=>{
            selection_array.push({
                "node": d,
                "drawChildren": true
            });
            d.in_selection_array = true;
        });
        source.in_selection_array = true;
        for(let i = 0; i < source.all_children.length; i++){
            selection_array.push({
                "node": source.all_children[i],
                "drawChildren": true
            });
            source.all_children[i].in_selection_array = true;
        }
        // add other nodes according to doi
        let all_node = [];
        let first_not_visited_node = 0;
        all_node.push(root);
        while(first_not_visited_node !== all_node.length){
            let visited_node = all_node[first_not_visited_node];
            first_not_visited_node ++;
            if (visited_node.all_children){
                for(let i = 0; i < visited_node.all_children.length; i++ ){
                    all_node.push(visited_node.all_children[i]);
                }
            }
        }
        all_node.sort(function(a,b){return b.doi - a.doi;});
        for (let i = 0; i < all_node.length; i++){
            if (!all_node[i].in_selection_array){
                selection_array.push({
                    "node": all_node[i],
                    "drawChildren": true
                })
            }
        }

        // // remove redundant nodes in selection array: clickQueue.removeRedundantNodes in tree.cut.js
        // for (let i = selection_array.length - 1; i >= 1; i--){
        //     if (inPath(source, selection_array[i].node)){
        //         selection_array.splice(i, 1);
        //     }
        // }

        // // preserve nodes with top-k doi (optional)
        // selection_array.splice(5);

        return selection_array
    }

    function collapse(node) {
        //collapse all children, namely all children are stored in node.children and node._children is empty
            //TODO: junlin的版本中做了一个判断，但是不知道为何要做这个判断
        node.children = [];
        if (node.all_children.length > 0){
            node.all_children.forEach(collapse);
        }
    }

    // function update__children(node) {
    //     // update node._children according to node.children
    //     node._children = [];
    //     for (let i = 0; i < node.all_children.length; i++ ){
    //         if (node.children.indexOf(node.all_children[i]) < 0){
    //             node._children.push(node.all_children[i]);
    //         }
    //     }
    //     node.all_children.forEach(update__children);
    // }

    // // 判断两个节点是否是祖先和后代的关系（无先后）
    // function inPath(source, item) {
    //     let node = item;
    //     while (node != null) {
    //         if (node === source)
    //             return true;
    //         node = node.parent;
    //     }
    //     node = source;
    //     while (node != null) {
    //         if (node === item)
    //             return true;
    //         node = node.parent;
    //     }
    //     return false;
    // }
};

export {TreeCut, tree_layout, mini_tree_layout}