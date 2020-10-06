import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

function layoutSentenceDAGNodes(state) {
  let width = state.DAG.width
  let height = state.DAG.height - 50
  let unique_layers = [...new Set(state.neuronclusters.map(d => d.layer_id))]
  unique_layers.sort((a, b) => a - b)
  let layerlen = unique_layers.length
  let layers = unique_layers.map(d => ({
      layer_id: d,
      scale: (d.length ? 0.5 : 1.0) / layerlen,
  }))
  let edge_width = width / layerlen * (1 - state.config.networkview.layer.node_scale)
  let padding = state.config.networkview.node.padding.bottom
  state.neuronclusters.forEach(d => { d.width = 0; d.height = 0; })
  for (let i = 0; i < layers.length; ++i) {
      layers[i].width = width * layers[i].scale
      layers[i].x = i == 0 ? 50 : (layers[i - 1].x + layers[i - 1].width)
      layers[i].clusters = state.neuronclusters.filter(d => d.layer_id == layers[i].layer_id)
      let totsize = layers[i].clusters.map(d => d.size).reduce((a, b) => a + b, 0)
      let h0 = 50
      let n = layers[i].clusters.length
      let lh = height - (n - 1) * padding
      if (n <= 3) {
          lh = height * 0.66;
          h0 = (height - lh) * 0.66;
      }
      layers[i].clusters.forEach(d => {
          d.scale = 1.0 / layers[i].clusters.length
          d.height = Math.max(padding * 2.5, lh * d.size / totsize)
          d.show_cloud = true
          d.width = layers[i].width - edge_width
          d.x = layers[i].x
      })
      for (let j = 0; j < layers[i].clusters.length; ++j) {
          layers[i].clusters[j].y = j == 0 ? 50 : (layers[i].clusters[j - 1].y + layers[i].clusters[j - 1].height + padding)
      }
      if (layers[i].clusters[n - 1].y + layers[i].clusters[n - 1].height > height) {
          let totsize = layers[i].clusters.map(d => d.height).reduce((a, b) => a + b, 0)
          layers[i].clusters.forEach(d => d.height *= lh / totsize)
          for (let j = 0; j < layers[i].clusters.length; ++j) {
              layers[i].clusters[j].y = j == 0 ? h0 : (layers[i].clusters[j - 1].y + layers[i].clusters[j - 1].height + padding)
          }
      }
  }
  state.current_layers = layers
}

function layoutDAGEdges(state, layers) {
  for (let i = 0; i < layers.length; ++i) {
      layers[i].clusters.forEach(d => {
          if (d.in_edges && d.in_edges.length > 0) {
              let tot_weight = 0
              let height_threshold = 4
              let weight_threshold = 0
              let weights = []
              for (let e of d.in_edges) weights.push(state.edges[e].weight)
              let n = weights.length - 1
              weights.sort((a, b) => b - a)
              for (let k = Math.min(2, n); k <= n; ++k) {
                  if (k == n || weights[k] > weights[k + 1] * 1.5 || k > 4) {
                      weight_threshold = weights[k]
                      break
                  }
              }

              for (let e of d.in_edges) tot_weight += state.edges[e].weight
              weight_threshold = Math.min(weight_threshold, height_threshold / d.height * tot_weight)
              if (weights.length >= 2 && weight_threshold < weights[1]) {
                  weight_threshold = weights[1]
              }

              for (let e of d.in_edges) {
                  if (state.edges[e].weight < weight_threshold && !state.edges[e].is_straight) {
                      tot_weight -= state.edges[e].weight
                      state.edges[e].weight = 0
                  }
              }
              tot_weight = 0
              for (let e of d.in_edges) tot_weight += state.edges[e].weight

              let curr_weight = 0
              for (let e of d.in_edges) {
                  state.edges[e].x2 = d.x
                  state.edges[e].y3 = d.y + d.height * (curr_weight / tot_weight)
                  curr_weight += state.edges[e].weight
                  state.edges[e].y4 = d.y + d.height * (curr_weight / tot_weight)
              }
          }
      })
  }
  for (let i = 0; i < layers.length; ++i) {
      layers[i].clusters.forEach(d => {
          if (d.out_edges && d.out_edges.length > 0) {
              for (let j = 0; j < d.out_edges.length; ++j) {
                  let e = d.out_edges[j]
                  state.edges[e].x1 = d.x + d.width
                  state.edges[e].y1 = j == 0 ? d.y : (state.edges[d.out_edges[j - 1]].y2)
                  state.edges[e].y2 = state.edges[e].y1 + (state.edges[e].y4 - state.edges[e].y3)
              }
              let last = d.out_edges[d.out_edges.length - 1]
              if (state.edges[last].y2 > d.y + d.height) {
                  let scale = d.height / (state.edges[last].y2 - d.y)
                  for (let j = 0; j < d.out_edges.length; ++j) {
                      let e = d.out_edges[j]
                      state.edges[e].y1 = (state.edges[e].y1 - d.y) * scale + d.y
                      state.edges[e].y2 = (state.edges[e].y2 - d.y) * scale + d.y
                      state.edges[e].y4 = (state.edges[e].y4 - state.edges[e].y3) * scale + state.edges[e].y3
                  }
              }
          }
      })
  }
  for (let i = 0; i < layers.length; ++i) {
      layers[i].clusters.forEach(d => {
          for (let j = 0; j < d.in_edges.length; ++j) {
              let e = d.in_edges[j]
              let h = state.edges[e].y4 - state.edges[e].y3
              state.edges[e].y3 = j == 0 ? d.y : (state.edges[d.in_edges[j - 1]].y4)
              state.edges[e].y4 = state.edges[e].y3 + h
          }
      })
  }
  for (let i = 0; i < layers.length; ++i) {
      layers[i].clusters.forEach(d => {
          let last = d.in_edges.length - 1
          if (last < 0) return
          let e = d.in_edges[last]
          if (state.edges[e].y4 < d.y + d.height) {
              let delta = d.y + d.height - state.edges[e].y4
              delta = delta / 2
              for (let j = 0; j < d.in_edges.length; ++j) {
                  let e = d.in_edges[j]
                  state.edges[e].y3 += delta
                  state.edges[e].y4 += delta
              }
          }
      })
      layers[i].clusters.forEach(d => {
          let last = d.out_edges.length - 1
          if (last < 0) return
          let e = d.out_edges[last]
          if (state.edges[e].y2 < d.y + d.height) {
              let delta = d.y + d.height - state.edges[e].y2
              delta = delta / 2
              for (let j = 0; j < d.out_edges.length; ++j) {
                  let e = d.out_edges[j]
                  state.edges[e].y1 += delta
                  state.edges[e].y2 += delta
              }
          }
      })
  }
}


export default new Vuex.Store({
  state: {
    server_url: 'http://166.111.81.49:5003',
    DAG: {},
    linechart: {},
    scatterplot: {},
    bubble: {
      left: 30,
      top: 10,
    },
    config: {
      linechart: {
        scale: 0.3,
        padding: 20,
      },
      animation: {
        
      },
      max_layers: 5,
      networkview: {
        padding: {
          x: 10,
          y: 5,
        },
        DAG: {
          padding: {
            top: 5,
          },
          scale: 0.7,
        },
        layer: {
          node_scale: 0.7,
        },
        node: {
          padding: {
            bottom: 10,
          }
        }
      },
      data_table: {
        max_table_len: 100,
        min_text_len: 30,
        target_text_len: 45,
      }
    },
    color_scheme: ["#cab2d6", "#fdbf6f", "#ffff99", "#b2df8a", "#a6cee3"],
    neuronclusters: [],
    edges: [],
    showed_layers: [0,3,6,9,10,12],
    layers: [1,2,3,4,5,6,7,8,9,10,11,12],
    current_layers: [],
    current_viewtype: 'sentence',
    layout: null,
    sentenceclusters: [],
    all_samples: [],
    current_samples: [],
    word_indexs: {},
    filtered_words: [],
    tooltip: {
      top: 0,
      left: 0,
      show: false,
      content: '',
    }
  },
  getters: {
    getSample: (state) => (idx) => {
      return state.all_samples[idx]
    },
    getSamples: (state) => (idxs) => {
      let ret
      const max_len = state.config.data_table.max_table_len
      const target_len = state.config.data_table.target_text_len
      if (!!idxs) {
        ret = idxs.map(idx => state.all_samples[idx])
          .sort((a, b) => Math.abs(a.text.length - target_len) - Math.abs(b.text.length - target_len))
          .slice(0, max_len)
      } else {
        ret = state.all_samples
          .filter(d => d.text.length > state.config.data_table.min_text_len)
          .slice(0, max_len)
          .sort((a, b) => Math.abs(a.text.length - target_len) - Math.abs(b.text.length - target_len))
      }
      return ret
    },
    getWordIdxs: (state) => (key) => {
      return state.word_indexs[key]
    },
    view_samples: (state) => {
      let oldidxs = new Set(state.current_samples.map(d => d.index))
      let newidxs = new Set()
      for (let word of state.filtered_words) {
        for (let idx of state.word_indexs[word]) {
          newidxs.add(idx)
          if (oldidxs.has(idx)) {
            oldidxs.delete(idx)
          }
        }
      }
      let filtered_set = new Set(state.filtered_words)
      let idxs = [...newidxs].concat([...oldidxs])
      let ret = idxs.map(idx => state.all_samples[idx])
        .map(d => {
          let words = []
          for (let text of d.text.split(' ')) {
            let flag = 1
            for (let word of state.filtered_words) {
              if (text.indexOf(word) != -1) {
                flag = 0
                let p = text.indexOf(word)
                if (p > 0) {
                  words.push([text.slice(0, p), false])
                }
                words.push([word, true])
                if (word.length + p < text.length) {
                  words.push([text.slice(word.length + p), false])
                }
                break
              }
            }
            if (flag) {
              words.push([text, false])
            }
          }
          return {
            index: d.index,
            text: words,
            label: d.label,
            score: d.score,
          }
        })
      // console.log('view_samples', ret)
      return ret
    }
  },
  mutations: {
    selectClass(state, label1, label2) {

    },
    updatePosition(state, payload) {
      const width = payload.network.width - state.config.networkview.padding.x * 2
      const height = payload.network.height - state.config.networkview.padding.y * 2
      state.bubble.width = payload.bubble.width
      state.bubble.height = payload.bubble.height
      state.linechart.width = payload.linechart.width - state.config.networkview.padding.x
      state.linechart.height = payload.linechart.height - state.config.networkview.padding.y
      state.linechart.x = state.config.networkview.padding.x
      state.linechart.y = state.config.networkview.padding.y
      state.DAG.width = width
      state.DAG.height = height - state.config.networkview.DAG.padding.top
      state.DAG.x = state.config.networkview.padding.x
      state.DAG.y = state.config.networkview.DAG.padding.top
    },
    setViewtype(state, type) {
      state.current_viewtype = type
    },
    set_scatterplot(state, payload) {
      state.scatterplot = payload.data
    },
    setLayers(state, data) {
      state.layers = data
    },
    calcEdges(state, layers) {
      layoutDAGEdges(state, layers)
    },
    calcDAG(state) {
      if (state.current_viewtype == 'word') {
        layoutSentenceDAGNodes(state)
        this.commit('calcEdges', state.current_layers)
      }
    },
    changeFilteredWord(state, key) {
      const idx = state.filtered_words.indexOf(key)
      if (idx != -1) {
        state.filtered_words.splice(idx, 1)
      } else {
        state.filtered_words.push(key)
      }
    },
    setNetwork(state, payload) {
      if (state.current_viewtype == 'sentence') {
        state.layout = payload.data.layout
      } else if (state.current_viewtype == 'word') {
        state.neuronclusters = payload.data.neuron_clusters
        state.edges = payload.data.edges
      }
      //console.log(state.neuronclusters)
    },
    setAllSamples(state, data) {
      state.all_samples = data.sort((a, b) => a.id - b.id)
    },
    setCurrentSamples(state, data) {
      console.log(data)
      state.current_samples = data
    },
    setWordIndex(state, { key, idxs }) {
      state.word_indexs[key] = idxs
    },
    showTooltip(state, { top, left, content }) {
      state.tooltip.top = top + 10
      state.tooltip.left = left + 10
      state.tooltip.content = content
      state.tooltip.show = true
    },
    hideTooltip(state) {
      state.tooltip.show = false
    }
  },
  actions: {
    async fetchWordIndex({ commit, state }, key) {
      if (!!state.word_indexs[key]) {
        return
      }
      const resp = await axios.post(`${state.server_url}/api/word`, { word: key })
      const idxs = resp.data.idxs
      commit('setWordIndex', { key, idxs })
    },
    async fetchLayerInfo({ commit, state }, { idxs, attrs }) {
      const resp = await axios.post(`${state.server_url}/api/layers`, { idxs, attrs })
      commit('setLayers', resp.data)
    },
    async fetchDAG({ commit, state }, req) {
      let resp = await axios.post(`${state.server_url}/api/networks`, req)
      commit('setNetwork', resp)
      commit('calcDAG')
    },
    async fetchAllSample({ commit, state, getters }) {
      let resp = await axios.post(`${state.server_url}/api/all_sentences`, { })
      // console.log(resp.data.sentences)
      commit('setAllSamples', resp.data.sentences)
      commit('setCurrentSamples', getters.getSamples(null))
    }
  },
  modules: {
  }
})