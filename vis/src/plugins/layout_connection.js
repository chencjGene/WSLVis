const ConnectionLayout = function(parent, cluster_association_mat){
    let that = this;
    that.parent = parent;
    that.cluster_association_mat = cluster_association_mat;
    console.log("pass in connection layout", cluster_association_mat);

    this.get_cluster_association_mat = function(){
        return that.parent.cluster_association_mat;
    }

    this.update = function(text_node, image_node){
        let text_idxs = text_node.map(d => d.data.descendants_idx ? d.data.descendants_idx: [d.id]);
        let image_idxs = image_node.map(d => d.data.descendants_idx ? d.data.descendants_idx: [d.id]);
        let text_num = text_idxs.length;
        let image_num = image_idxs.length;
        that.matrix = [];
        for (let i = 0; i < text_num; i++){
            that.matrix.push([]);
            for (let j = 0; j < image_num; j++){
                let element = 0;
                for (let s = 0; s < text_idxs[i].length; s++){
                    for (let t = 0; t < image_idxs[j].length; t++){
                        element += that.get_cluster_association_mat()[text_idxs[i][s]][image_idxs[j][t]];
                    }
                }
                that.matrix[i].push(element);
            }
        }
    };
}

export {ConnectionLayout};