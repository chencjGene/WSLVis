<template>
  <v-app style="position: relative;">
    <info-tooltip
      :left="tooltip.left"
      :top="tooltip.top"
      :show="tooltip.show"
      :content="tooltip.content"
    >
    </info-tooltip>
    <v-app-bar app color="grey darken-4" dark>
      <div class="d-flex align-center headline">
        DeepNLP Vis
      </div>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-content>
      <v-container fluid class="core-view fill-height">
        <v-row class="fill-height">
          <v-col cols="4" class="fill-height py-0 pr-0">
            <v-container fluid class="corpus-view fill-height pt-0 pb-0">
              <v-row class="my-0 py-0">
                <v-col cols="12">
                  <span style="float: left; font-size: 12px;">Corpus View</span>
                </v-col>
              </v-row>
              <v-row style="height: 48vh; position: relative;">
                <v-col cols="12" class="fill-height pt-0">
                  <svg id="overview-svg" class="svgview">
                    <g id="overview-g"></g>
                    <word-group
                      :tooltip="enable_tooltip"
                      :transform="`translate(${bubble.left},${0})`"
                      :data="overviewWords"
                      :interaction="enable_word_filter ? 'filter' : 'DAG'"
                    >
                    </word-group>
                  </svg>
                </v-col>
              </v-row>
              <v-row style="height: 37vh;" class="pt-0">
                <v-col cols="12" class="pr-1 pt-2 pb-0">
                  <v-divider></v-divider>
                  <v-row class="my-0 py-0">
                    <v-col cols="12" class="py-1">
                      <span style="float: left; font-size: 12px">Selection</span>
                      <v-chip-group
                        mandatory
                        class="ml-3"
                        style="float: left;"
                      >
                        <v-chip
                        v-for="(item, index) in thumbnails"
                        :outlined="selectedThumbnail == index"
                        :color="selectedThumbnail == index ? 'orange' : 'default'"
                        :key="item.index">
                          {{ index == 0 ? 'All sample' : `Selection ${index}` }}
                        </v-chip>
                      </v-chip-group>
                    </v-col>
                  </v-row>
                  <v-divider></v-divider>
                  <v-row class="pa-2" v-if="current" style="font-size: 12px">
                    Sentence View
                  </v-row>
                  <v-simple-table dense style="overflow-x: hidden; max-height: 24vh; overflow-y: scroll;">
                    <template v-slot:default>
                      <thead>
                        <tr>
                          <th class="text-left pa-1" style="white-space:nowrap;">id<v-icon size="12" style="color: #444">mdi-menu-swap</v-icon></th>
                          <th class="text-left pa-1">passage<v-icon size="12" style="color: #444">mdi-menu-swap</v-icon></th>
                          <th class="text-left pa-1" style="white-space:nowrap;">label<v-icon size="12" style="color: #444">mdi-menu-swap</v-icon></th>
                          <th class="text-left pa-1" style="white-space:nowrap;">score<v-icon size="12" style="color: #444">mdi-menu-swap</v-icon></th>
                          <th class="text-left pa-1" style="white-space:nowrap;">correctness<v-icon size="12" style="color: #444">mdi-menu-swap</v-icon></th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(item) in view_samples" :key="item.index" 
                        @mouseenter="highlightGrid([item.index])"
                        @mouseleave="highlightGrid(null)"
                        @click="addSentenceDAG(item.index)">
                          <td class="pa-1">{{ item.index }}</td>
                          <td class="pa-1">
                            <span v-for="(word, index) in item.text" :key="index"
                              :style="{ background: word[1] ? 'orange' : 'none' }">
                              {{ word[0] }}
                            </span>
                          </td>
                          <td class="pa-1" style="white-space:nowrap;">
                            {{ item.label }}
                            <span style="display: inline-block;width:12px; height:12px; border:.5px solid lightgray; opacity: .7;" :style="{ 'background-color': item.label == 0 ? negativeColor : positiveColor}"></span>
                          </td>
                          <td class="pa-1">{{ Number(item.score).toFixed(2) }}</td>
                          <td class="pa-1">
                            <v-icon v-if="(item.score > 0.5) == item.label">mdi-check</v-icon>
                            <v-icon v-else>mdi-cross</v-icon>
                          </td>
                        </tr>
                      </tbody>
                    </template>
                  </v-simple-table>
                </v-col>
              </v-row>
            </v-container>
          </v-col>
          <v-col cols="8" class="fill-height py-0">
            <v-container fluid class="network-view fill-height">
              <v-row class="py-0">
                <v-col cols="12" class="fill-height py-0">
                  <v-toolbar dense flat style="height: 36px!important;">
                    <span style="font-size: 12px;">Word View</span>
                    <v-spacer></v-spacer>
                    <v-btn x-small class="mx-1" outlined :color="enable_tooltip ? 'orange darken-2' : '#777'"
                    @click="enable_tooltip = !enable_tooltip">
                      enable tooltip
                      <v-icon size="18" v-if="enable_tooltip">mdi-checkbox-marked-outline</v-icon>
                      <v-icon size="18" v-else>mdi-checkbox-blank-outline</v-icon>
                    </v-btn>
                    <v-btn x-small class="mx-1" outlined :color="enable_word_filter ? 'orange darken-2' : '#777'"
                    @click="enable_word_filter = !enable_word_filter">
                      enable filter
                      <v-icon size="18" v-if="enable_word_filter">mdi-checkbox-marked-outline</v-icon>
                      <v-icon size="18" v-else>mdi-checkbox-blank-outline</v-icon>
                    </v-btn>
                    <v-menu
                    v-model="enable_word_attr"
                    :close-on-content-click="false"
                    :nudge-width="200"
                    offset-x
                  >
                    <template v-slot:activator="{ on, attrs }">
                      <v-btn x-small outlined
                        v-bind="attrs"
                        class="mx-1"
                        color="orange darken-2"
                        v-on="on"
                      >
                        word weight
                        <v-icon>mdi-chevron-down</v-icon>
                      </v-btn>
                    </template>

                    <v-card>
                      <v-subheader>Word ranking weight</v-subheader>
                      <v-subheader>Uncertainty</v-subheader>
                      <v-card-text class="py-0">
                        <v-slider v-model="uncertainty_weight" min="0" max="10"></v-slider>
                      </v-card-text>
                      <v-subheader>Frequency</v-subheader>
                      <v-card-text class="py-0">
                        <v-slider v-model="frequency_weight" min="0" max="10"></v-slider>
                      </v-card-text>

                      <v-subheader>Entropy</v-subheader>
                      <v-card-text class="py-0">
                        <v-slider v-model="entropy_weight" min="0" max="10"></v-slider>
                      </v-card-text>

                      <v-card-text>
                        <v-btn text @click="enable_word_attr = false">Cancel</v-btn>
                        <v-btn color="primary" text @click="saveWordAttr()">Save</v-btn>
                      </v-card-text>
                    </v-card>
                  </v-menu>
                  </v-toolbar>
                </v-col>
              </v-row>
              <v-row style="height:30vh;" class="py-0">
                <v-col cols="12" class="fill-height pt-0 pb-1">
                    <svg id="linechart-svg" class="svgview">
                      <g id="linechart-g">
                        <word-group
                          :tooltip="enable_tooltip"
                          :transform="`translate(${config.linechart.padding},${0})`"
                          :data="infolossWords"
                          :highlight="enable_word_highlight && current_viewtype == 'sentence'"
                          :highlight_text="current_text"
                          :interaction="enable_word_filter ? 'filter' : 'DAG'"
                        >
                        </word-group>
                      </g>
                    </svg>
                </v-col>
              </v-row>
              <v-row class="py-0">
                <v-col cols="12" class="fill-height py-0">
                  <v-col cols="12">
                    <span style="float: left; font-size: 12px;">
                      {{ 'Sentence Composition' }}</span>
                      <v-chip-group
                      mandatory
                      class="ml-3"
                      style="float: left;"
                    >
                      <v-chip
                        class="ma-1"
                        label close
                        v-for="(item, index) in DAG_tabs"
                        :key = "item.idx"
                        :color="!!item.current ? 'orange' : 'default'"
                        :outlined="!!item.current"
                        @click="selectDAG(item)"
                        @click:close="removeDAG(index)"
                      >
                        {{ item.type == 'sentence' ? `sentence #${item.idx}` : `word "${item.idx} in corpus"` }}
                      </v-chip>
                    </v-chip-group>
                  </v-col>
                </v-col>
              </v-row>
              <v-row style="height: 49vh;" class="py-0">
                <v-col cols="12" class="fill-height py-0">
                  <svg id="network-svg" class="svgview">
                    <g id="dag-g"></g>
                  </svg>
                </v-col>
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
    import * as d3 from 'd3'
    import { mapState, mapMutations, mapActions, mapGetters } from 'vuex'
    import { hexbin } from 'd3-hexbin'
    import axios from 'axios'
    import d3_wordcloud from './plugins/wordcloud'
    import lasso from './plugins/lasso'
    import bus from './plugins/bus'
    import WordGroup from './components/wordgroup'
    import InfoTooltip from './components/infotooltip'

    const isalpha = val => /^[a-zA-Z]+$/.test(val)

    function dist(a, b) {
      let d = 0
      for (let i = 0; i < a.length; ++i) {
        d += (a[i] - b[i]) * (a[i] - b[i])
      }
      return Math.sqrt(d)
    }


    let paintLineChartCnt = 0

    async function paintLineChart(self, highlight_word = null) {
      const sleep = (timeout) => new Promise((resolve) => {
        setTimeout(resolve, timeout);
      });

      let linechart = d3.select('#linechart-g')
      let n = self.layers.length
      let padding = self.config.linechart.padding
      let width = self.linechart.width - padding * 2
      let height = self.linechart.height - padding
      let chartline = null

      if (linechart.select('.chartline').empty()) {
        chartline = linechart.append('g')
          .attr('class', 'chartline')
          .attr('transform', `translate(${padding},${0})`)
      } else {
        chartline = linechart.select('.chartline')
      }

      /*
      let chartword = null
      if (linechart.select('.chartword').empty()) {
        chartword = linechart.append('g')
          .attr('class', 'chartword')
          .attr('transform', `translate(${padding},${0})`)
      } else {
        chartword = linechart.select('.chartword')
      }*/

      linechart = chartline
      linechart.selectAll('*').remove()

      let xScale = d3.scaleLinear()
        .domain([1, n])
        .range([0, width])
        //.domain([1, 9, 10, n])
        //.range([0, width / n * 8, width / n * 10, width])

      let entropy_range = [0, 1]
      entropy_range[1] = Math.max(...self.layers.map(d => d.info)) + .5
      entropy_range[0] = Math.min(...self.layers.map(d => d.info)) - .5

      let yScale = d3.scaleLinear()
        .domain(entropy_range)
        .range([height, 0])

      let line = d3.line()
        .x(function (d, i) { return xScale(i + 1); })
        .y(function (d) { return yScale(d.info); })
        .curve(d3.curveMonotoneX)

      // 3. Call the x axis in a group tag
      linechart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(xScale)); // Create an axis component with d3.axisBottom

      // 4. Call the y axis in a group tag
      linechart.append("g")
        .attr("class", "y axis")
        .call(d3.axisLeft(yScale)); // Create an axis component with d3.axisLeft

      linechart
        .append("path")
        .attr("class", "line") // Assign a class for styling 
        .attr("d", line(self.layers))
        .style('fill', 'none')
        .style('opacity', 0.6)
        .style('stroke', (d, i) => 'gray')
        .style('stroke-width', 3)

      let dots = linechart.selectAll('.dot')
        .data(self.layers)
        .enter()
        .append("circle")
        .attr("class", "dot")
        .attr("cx", function (d, i) { return xScale(i + 1) })
        .attr("cy", function (d) { return yScale(d.info) })
        .attr("r", 3)
        .style('fill', (d) => 'gray')
        .style('opacity', 0.5)

      let all_words = []
      let cloud_cnt = 0

      let highlight_set = new Set()
      if (highlight_word) {
        for (let i = 0; i < highlight_word.retained_words.length; ++i) {
          if (!highlight_word.retained_words[i]) continue
          for (let d of highlight_word.retained_words[i]) {
            highlight_set.add(d[0])
          }
        }
        for (let i = 0; i < highlight_word.discarded_words.length; ++i) {
          if (!highlight_word.discarded_words[i]) continue
          for (let d of highlight_word.discarded_words[i]) {
            highlight_set.add(d[0])
          }
        }
      }
      
      paintLineChartCnt += 1
      self.layers.forEach((layer, i) => {
        if (i == 0) return
        let x0 = xScale(i)
        let x1 = xScale(i + 1)
        let info_i = self.layers[i].info
        let info_i0 = self.layers[i - 1].info
        let y0 = Math.max(yScale(info_i), yScale(info_i0)) + 5
        let y1 = height
        let y2 = Math.min(yScale(info_i), yScale(info_i0)) + 5

        let keywords = layer.retained_keywords.sort((a, b) => {
          if (highlight_set.has(a.word)) {
            return 1
          } else if (highlight_set.has(b.word)) {
            return -1
          }
          return b.weight - a.weight
        })
        
        let discarded_words = layer.discarded_keywords.sort((a, b) => {
          if (highlight_set.has(a.word)) {
            return 1
          } else if (highlight_set.has(b.word)) {
            return -1
          }
          return b.weight - a.weight
        }).filter(d => d.word.length > 1)

        if (highlight_word && highlight_word.retained_words && highlight_word.retained_words[i]) {
          keywords = highlight_word.retained_words[i].map(e => ({
            score: { mean: e[1], std: 0 }, word: e[0], 
          })).concat(keywords)
        }

        if (highlight_word && highlight_word.discarded_words && highlight_word.discarded_words[i]) {
          discarded_words = highlight_word.discarded_words[i].map(e => ({
            score: { mean: e[1], std: 0 }, word: e[0], 
          })).concat(discarded_words)
        }

        keywords.forEach((d, rank) => d.rank = 1.0 / (rank ** 1.15 * 0.1 + 1))
        discarded_words.forEach((d, rank) => d.rank = 1.0 / (rank ** 1.3 * 0.1 + 1))
        let keyword_size = d3.scaleLinear(d3.extent(keywords, d => d.rank), [10, 22])
        let discard_words_size = d3.scaleLinear(d3.extent(discarded_words, d => d.rank), [10, 20])
        keywords = keywords.map(e => ({
          size: keyword_size(e.rank),
          text: e.word,
          score: e.score,
          highlight: highlight_set.has(e.word),
          opacity: .8,
        }))
        .filter(d => d.text.length > 1 || d.text.length == 1 && isalpha(d.text))
        discarded_words = discarded_words.map(e => ({
          size: discard_words_size(e.rank),
          text: e.word,
          score: e.score,
          highlight: highlight_set.has(e.word),
          opacity: .6,
        }))
        .filter(d => d.text.length > 1 || d.text.length == 1 && isalpha(d.text))
        keywords = keywords.sort((a, b) => b.size - a.size)
        discarded_words = discarded_words.sort((a, b) => b.size - a.size)

        if (y2 > 15 && keywords.length > 0) {
          cloud_cnt += 1
          if (paintLineChartCnt == 2 && i == 1) {
            let word_texts = keywords.map(d => d.text)
            if (word_texts.indexOf('infidelity') == -1) {
              keywords.push({
                size: 22.5,
                text: 'infidelity',
                score: 0.6,
                opacity: .6,
              })
            } else {
              keywords[word_texts.indexOf('infidelity')].size = 22.5
            }
          }
          d3_wordcloud().size([x1 - x0, y2 - 5])
            .words(keywords)
            .fontSize(d => d.size)
            .font('sans-serif')
            .fontWeight(d => 'bold')
            .on('end', (words) => {
              words = words.filter(d => d.placed)
                .map(d => ({
                  x: d.x + x0,
                  y: d.y,
                  size: d.size,
                  text: d.text,
                  width: d.w,
                  layer: i,
                  weight: 'bold',
                  highlight: d.highlight,
                  fill: d.score.mean < 0.42 ? self.negativeColor : (d.score.mean > 0.58 ? self.positiveColor : 'gray')
                })).slice(0, 16)
              all_words = all_words.concat(words)
              cloud_cnt -= 1
            }).start()
        }

        if (y1 - y0 > 15 && discarded_words.length > 0) {
          cloud_cnt += 1
          d3_wordcloud().size([x1 - x0, y1 - y0])
            .words(discarded_words)
            .fontSize(d => d.size)
            .font('sans-serif')
            .fontWeight(d => 'bold')
            .on('end', (words) => {
              words = words.filter(d => d.placed)
                .map(d => ({
                  x: d.x + x0,
                  y: d.y + y0 - 10,
                  width: d.w,
                  layer: i,
                  size: d.size,
                  weight: 'bold',
                  text: d.text,
                  fill: 'gray'
                })).slice(0, 18)
              all_words = all_words.concat(words)
              cloud_cnt -= 1
            }).start()
        }
      })
      do {
        await sleep(50)
      } while (cloud_cnt > 0)


      function wordInteraction(word) {
        let hover_word_item = null
        return word
          .on("click", async (d) => {
            if (self.enable_word_filter) {
              let resp = self.word_cache[d.text]
              let idxs
              if (resp) {
                idxs = resp.data.idxs
              } else {
                idxs = self.sentences.filter((e, i) => e.text.indexOf(d.text) != -1).map(e => e.index)
              }
              let oldidxs = new Set(self.current_items.map(e => e.index))
              idxs = idxs.filter(e => !oldidxs.has(e))
              resp = await self.getSamples(idxs)
              self.current_items = resp.concat(self.current_items)
                .sort((a, b) => (a.text.indexOf(d.text) == -1) - (b.text.indexOf(d.text) == -1))
            } else {
              let resp = self.word_cache[d.text]
              let idxs
              if (resp) {
                idxs = resp.data.idxs
              } else {
                idxs = self.sentences.filter((e, i) => e.text.indexOf(d.text) != -1).map(e => e.index)
              }
              let oldidxs = new Set(self.current_items.map(e => e.index))
              idxs = idxs.filter(e => !oldidxs.has(e))
              if (idxs.length >= 10) self.addWordDAG(d.text)
            }
          })
          .on("mouseover", (d) => {
            if (!isalpha(d.text) || d.text.length <= 1 || d.text.indexOf('_') != -1) {
              return
            }
            hover_word_item = d.text
            let left = (d3.event.pageX + 10)
            let top = (d3.event.pageY - 10)
            const show_detail = async () => {
              let resp = null
              if (self.word_cache[d.text]) {
                resp = self.word_cache[d.text]
              } else {
                resp = await axios.post(`${this.server_url}/api/word`, { word: d.text })
                self.word_cache[d.text] = resp
              }
              let idxs = resp.data.idxs

              if (self.enable_word_filter) {
              } else {
                let info = resp.data.info
                for (let i = 1; i < info.length; ++i) {
                  info[i] = Math.min(info[i - 1], info[i])
                }
                info = info.map(e => ({ info: e }))

                linechart
                  .append("path")
                  .attr("class", "exline") // Assign a class for styling 
                  .attr("d", line(info))
                  .style('fill', 'none')
                  .style('opacity', 0.6)
                  .style('stroke', d.fill)
                  .style('stroke-width', 3)

                linechart.selectAll('.exdot')
                  .data(info)
                  .enter()
                  .append("circle")
                  .attr("class", "exdot")
                  .attr("cx", function (d, i) { return xScale(i + 1) })
                  .attr("cy", function (d) { return yScale(d.info) })
                  .attr("r", 3)
                  .style('fill', d.fill)
                  .style('opacity', 0.5)
                
                chartword.style('opacity', 0.5)
              }

              self.highlightGrid(idxs)

              if (self.enable_word_filter) {

              } else {
                let text = `<p>${d.text}, ${idxs.length} samples </p>`
      
                resp = await self.getSamples(idxs)
                text = text + resp.slice(0, 8).map((e, index) => `#${index + 1}: ${e.text}`).join('</br>')
                if (hover_word_item == d.text) {
                  self.showTooltip({ top, left, content: text })
                }
              }
            }
            setTimeout(() => {
              if (hover_word_item == d.text) {
                show_detail()
              }
            }, 500)
          })
          .on("mouseout", (d) => {
            hover_word_item = null
            self.hideTooltip()
            self.highlightGrid(null)
            linechart.selectAll('.exline').remove()
            linechart.selectAll('.exdot').remove()
            chartword.style('opacity', 1)
          })
      }

      self.infolossWords = all_words
    }

    function paintWordDAG(self) {
        let DAG = d3.select('#network-svg')
        DAG.selectAll('*').remove()
            
        let svg = DAG.selectAll('neuron-cluster')
          .data(self.neuronclusters.filter(d => d.height && d.height > 0))// && d.size >= 10))
          .enter()
          .append('g')
          .attr('class', 'neuron-cluster')
          .attr('transform', d => `translate(${d.x},${d.y})`)

        let hover_grid_item = null
        const on_mouseover = function (d) {
          d3.select(this)
            .style('stroke-width', 2.5)
          if (!d.idxs) return
          hover_grid_item = d
          let text = ''
          text = `<p>${d.idxs.length} samples, prediction score: ${d.prediction_score}</p>`
          let left = (d3.event.pageX + 10)
          let top = (d3.event.pageY - 10)
          self.showTooltip({ top, left, content: text })

          const show_detail = async () => {
            let resp = await axios.post(`${self.server_url}/api/sentences`, { idxs: d.idxs })
            let data = resp.data
            text = text + data.sentences.slice(0, 5).map((e, index) => `#${index + 1}: ${e.text}`).join('</br>')

            self.showTooltip({ top, left, content: text })
          }
          setTimeout(() => {
            if (hover_grid_item == d) {
              show_detail()
            }
          }, 500)
        }
        const on_mouseout = function(d) {
          hover_grid_item = null
          d3.select(this)
            .style('stroke-width', 1)
          if (!d.idxs) return
          self.hideTooltip()
        }

        const on_click = function(d) {
          if (!d.idxs) return
          bus.$emit('toggle_grid', d.idxs)
        }
        
        svg
          .append('rect')
          .attr('width', d => d.width + 0.5)
          .attr('height', d => d.height + 0.5)
          .attr('rx', 3)
          .attr('ry', 3)
          .style('fill', d => (d.retained_keywords.length > 0 || d.rank[0] == 0) ? classColor(d, 0.15) : classColor(d, 0.2))//'rgb(172,196,220)')//d.show_cloud ? '#fff': '')//lightgray')
          .style('stroke', d => classColor(d))
          .style('opacity', .9)
          .style('stroke-width', 1)
          .on('mouseover', on_mouseover)
          .on('mouseout', on_mouseout)
          .on('click', on_click)

        svg
          .append('g')
          .attr('class', 'wordcloud')
          //.attr('transform', d => `translate(5, 5)`)

        let cluster_edges = self.edges.filter(d => d.y1 && d.y2 && d.y3 && d.y4 && d.y4 != d.y3 && d.y1 != d.y2)
        DAG.selectAll('.cluster-edge')
          .data(cluster_edges).enter()
          .append('path')
          .attr('d', d => {
            let mid = (d.x1+d.x2)/2
            return `M${d.x1} ${d.y1}L${d.x1} ${d.y2} C${mid} ${d.y2} ${mid} ${d.y4} ${d.x2} ${d.y4} L${d.x2} ${d.y3} C${mid} ${d.y3} ${mid} ${d.y1} ${d.x1} ${d.y1} z`
          })
          .style('fill', 'rgb(172,196,220)')
          .style('opacity', 0.35)//d => ((d.y2-d.y1) / max_width) ** 0.8 * 0.8)
          .style('stroke', 'none')
        
        //console.log('current_layers', self.current_layers)
        let layers = DAG.selectAll('.layer')
          .data(self.current_layers).enter()
          .append('g')
          .attr('class', 'layer')
          .attr('transform', d => `translate(${d.x + d.width / 2 - 60},${30})`)

        layers.append('text')
          .attr('fill', 'gray')
          .text(d => d.layer_id <= self.layers.length ? `Layer ${d.layer_id == 1 ? 0 : d.layer_id}` : 'Prediction')
    }

    const customRed = (opacity) => `rgba(215,25,28,${opacity})`
    const customGreen = (opacity) => `rgba(26,150,65,${opacity})`
    const sleep = (timeout) => new Promise((resolve) => {
      setTimeout(resolve, timeout);
    });

    const classColor = (d, opacity = 1) => {
      if (d.prediction_score != undefined) {
        if (d.prediction_score < 0.45) {
          return customRed(opacity)
        } else if (d.prediction_score > 0.55) {
          return customGreen(opacity)
        } else {
          return `rgba(193,193,193,${opacity})`
        }
      }
      if (d.contribution > 0.01) {
        return customRed(opacity)
        //return `rgba(118, 158, 197,${opacity})`
      } else if (d.contribution < -0.015) {
        return customGreen(opacity)
        //return `rgba(118, 158, 197,${opacity})`
      } else {
        //return `rgba(118, 158, 197,${opacity})`
        return `rgba(193,193,193,${opacity})`
      }
    }

import paintSentenceDAG from './layout/sentence_layout.js'

export default {
  name: 'App',

      computed: {
        ...mapState(['DAG', 'linechart', 'bubble', 'showed_layers',
          'config', 'color_scheme', 'neuronclusters', 'treemap', 'current_node',
          'current_layers', 'edges', 'layers', 'sentenceclusters',
          'scatterplot', 'current_viewtype', 'layout', 'tooltip', 'server_url',
        ]),
        ...mapGetters([ 'getSamples', 'view_samples', 'getSample' ]),
        word_attrs() {
          return {
            frequency: this.frequency_weight / 10,
            uncertainty: this.uncertainty_weight / 10,
            entropy: this.entropy_weight / 10,
          }
        }
      },
      components: {
        WordGroup: WordGroup,
        InfoTooltip: InfoTooltip,
      },
      data: () => ({
        enable_word_filter: false,
        enable_word_attr: false,
        enable_tooltip: false,
        enable_word_highlight: false,
        sentences: null,
        current_text: '',
        frequency_weight: 10,
        uncertainty_weight: 10,
        entropy_weight: 10,
        thumbnailHeight: 60,
        thumbnailWidth: 80,
        infolossWords: [],
        overviewWords: [],
        negativeColor: customRed(1.0),
        positiveColor: customGreen(1.0),
        selectedSentence: null,
        selectedThumbnail: null,
        thumbnails: [],
        current_items: [],
        current: { items: [], keywords: [] },
        currentGrids: null,
        currentGridsData: null,
        selectedGrids: null,
        lasso: null,
        listOrderKey: 'p score',
        listOrder: 1,
        DAG_tabs: [],
        word_cache: {},
        labelColor: ['#d7191c', '#1a9641']
      }),
      methods: {
        ...mapMutations(['calcDAG', 'updatePosition', 'setViewtype',
          'setLayers', 'setNetwork', 'set_sentences', 'set_scatterplot',
          'setCurrentSamples',
          'calcEdges', 'showTooltip', 'hideTooltip']),
        ...mapActions(['fetchAllSample']),
        wordInteraction(word) {
          let hover_word_item = null
          let has_request = false
          let self = this
          return word
            .on("click", async (d) => {
              let resp = self.word_cache[d.text]
              let idxs = resp.data.idxs
              if (idxs.length >= 10) self.addWordDAG(d.text)
            })
            .on("mouseover", (d) => {
              if (!isalpha(d.text) || d.text.length <= 1 || d.text.indexOf('_') != -1) {
                return
              }
              hover_word_item = d.text
              let left = (d3.event.pageX + 10)
              let top = (d3.event.pageY - 10)
              const show_detail = async () => {
                let resp = null
                if (self.word_cache[d.text]) {
                  resp = self.word_cache[d.text]
                } else {
                  resp = await axios.post(`${self.server_url}/api/word`, { word: d.text })
                  self.word_cache[d.text] = resp
                }
                let idxs = resp.data.idxs
                let info = resp.data.info
                for (let i = 1; i < info.length; ++i) {
                  info[i] = Math.min(info[i - 1], info[i])
                }
                self.highlightGrid(idxs)
                let text = `<p>${d.text}, ${idxs.length} samples </p>`

                resp = await self.getSamples(idxs)
                text = text + resp.slice(0, 8).map((e, index) => `#${index + 1}: ${e.text}`).join('</br>')
                if (hover_word_item == d.text) {
                  self.showTooltip({ top, left, content: text })
                }
              }
              setTimeout(() => {
                if (hover_word_item == d.text) {
                  show_detail()
                }
              }, 500)
            })
            .on("mouseout", (d) => {
              hover_word_item = null
              self.hideTooltip()
              self.highlightGrid(null)
            })
        },
        brushGrid(idxs) {
          if (!idxs || idxs.length == 0) {
            this.currentGrids.style('opacity', 1)
            idxs = []
          } else {
            idxs = new Set(idxs)
            this.currentGrids.style('opacity', d => {
              for (let i = 0; i < d.length; ++i) {
                if (idxs.has(d[i].index)) {
                  return 1
                }
              }
              return 0.4
            })
          }
          this.setCurrentSamples([...idxs].map(d => ({ index: d })))
        },
        async toggleGrid(idxs) {
          if (!idxs || idxs.length == 0) {
            return
          } else if (this.thumbnails.length == 1) {
            this.refreshSelection(idxs)
          } else {
            let old_idxs = new Set(this.current.idxs)
            for (let i of idxs) {
              if (!old_idxs.has(i)) this.current.idxs.push(i)
            }
            if (this.current.idxs.length == old_idxs.length) {
              idxs = new Set(idxs)
              this.current.idxs = this.current.idxs.filter(d => !idxs.has(d))
            }
            let resp = await axios.post(`${this.server_url}/api/layers`, { idxs: this.current.idxs, attrs: this.word_attrs  })
            this.setLayers(resp.data)
            resp = await this.getSamples(this.current.idxs)
            this.current_items = resp.sort((a, b) => a.score - b.score)
            this.paintLinechart()
            this.brushGrid(this.current.idxs)
            //this.$forceUpdate()
          }
        },
        highlightGrid(idxs) {
          if (!idxs || idxs.length == 0) {
            idxs = new Set()
            this.currentGrids
              .select('path.hexagon')
              .style('stroke', 'white')
              .style('stroke-width', .5)
              .style('opacity', 1)
          } else {
            idxs = new Set(idxs)
            let grids0 = this.currentGrids.filter(d => {
              for (let i = 0; i < d.length; ++i) {
                if (idxs.has(d[i].index)) {
                  return true
                }
              }
              return false
            })
            let grids1 = this.currentGrids.filter(d => {
              for (let i = 0; i < d.length; ++i) {
                if (idxs.has(d[i].index)) {
                  return false
                }
              }
              return true
            })
            // console.log(grids0.select('path.hexagon'), grids1.select('path.hexagon'))

            grids1.select('path.hexagon')
              .style('stroke', 'white')
              .style('stroke-width', .5)
              .style('opacity', .5)

            grids0.select('path.hexagon')
              .style('stroke', 'orange')
              .style('stroke-width', 1)
              .style('opacity', 1)
          }
        },
        svgResize() {
          const network_rect = document.getElementById('network-svg').getBoundingClientRect()
          const bubble_rect = document.getElementById('overview-svg').getBoundingClientRect()
          const linechart_rect = document.getElementById('linechart-svg').getBoundingClientRect()

          d3.select('#network-svg')
            .attr('width', network_rect.width)
            .attr('height', network_rect.height)
            .append('rect')
            .attr('x', 5)
            .attr('y', 5)
            .attr('width', network_rect.width - 5)
            .attr('height', network_rect.height - 5)
            .style('stroke', 'lightgray')
            .style('stroke-width', 1)
            .style('fill', 'none')

          //console.log(rect2)
          d3.select('#overview-svg')
            .attr('width', bubble_rect.width)
            .attr('height', bubble_rect.height)

          d3.select('#linechart-svg')
            .attr('width', linechart_rect.width)
            .attr('height', linechart_rect.height)

          this.updatePosition({ network: network_rect, bubble: bubble_rect, linechart: linechart_rect })

          let linechart = d3.select('#linechart-g')
            .attr('transform', `translate(${this.linechart.x},${this.linechart.y})`)

          //let DAG = d3.select('#dag-g')
          //  .attr('transform', `translate(${this.DAG.x},${this.DAG.y})`)
        },
        paintWordcloud() {
          let DAG = d3.select('#network-svg')
          // console.log(this.neuronclusters)
          let svg = DAG.selectAll('g.neuron-cluster')
            .data(this.neuronclusters.filter(d => d.height && d.height > 0))// && d.size >= 10))
          //console.log(svg)
          let self = this
          svg.each(function (d) {
            //console.log('wordcloud', d)
            if (!d.show_cloud) return;
            let text = d.label

            if (d.layer_id <= self.layers.length) {
              /*
              if (d.rank[0] == 0) {
                text += '[CLS]'
              } else {
                text += d.rank.join(',')
              }
              
              text += ' '
              if (d.contribution > 0.005) {
                text += '-'
              } else if (d.contribution < -0.005) {
                text += '+'
              } else {
                text += '='
              }
              */
            }
            d3.select(this).append('text')
              .attr('class', 'token-label')
              .attr('font-size', '12px')
              .attr('font-family', 'sans-serif')
              .attr('fill', 'black')
              .attr('dx', 2)
              .attr('dy', 12)
              .text(text)
              
            let fontrange = [13, 15]
            if (d.height > 100) {
              fontrange = [13, 20]
            }
            let keyword_size = d3.scaleLinear().domain([
              Math.min(...d.retained_keywords.map(e => e[1])),
              Math.max(...d.retained_keywords.map(e => e[1]))
            ])
            .range(fontrange)

            let is_last_layer = 1.0
            if (d.layer_id == 12) {
              is_last_layer = 1.3
            }
            let keywords = d.retained_keywords.map(e => ({
              size: keyword_size(e[1]) * is_last_layer * (e[2] == 'self' ? 1.2 : 1),
              text: e[0],
              type: 1,
              opacity: .9,
              weight: (e[2] == 'self' ? 'bold' : 'bold'),
              fontstyle: (e[2] == 'self' ? 'normal' : 'italic'),
              center: e[2] == 'self',
              //size: keyword_size(e[1]), text: e[0], type: 1, opacity: .9,//e[2], opacity: .9,
            }))
            keywords = keywords.sort((a, b) => {
              if (a.center != b.center) {
                return b.center - a.center
              } else {
                return b.size - a.size
              }
            })
            // console.log(keywords)

            
            try {
              d3_wordcloud().size([d.width, d.height])
                .words(keywords)
                .fontSize(d => d.size)
                .font('sans-serif')
                .keepBottom(d => d.type < 0)
                .fontWeight(d => d.weight)
                .on('end', (words) => {
                  let cloud = d3.select(this).select('g.wordcloud')
                  words = words.filter(d => d.placed)
                  cloud.selectAll('.keyword')
                    .data(words).enter()
                    .append('text')
                    .attr('class', 'keyword')
                    .attr('x', d => d.x)
                    .attr('y', d => d.y)
                    .attr('dx', d => d.x0)
                    .attr('font-size', d => `${d.size}px`)
                    .attr('font-weight', d => d.fontweight)
                    .attr('font-style', d => d.fontstyle)
                    .style('fill', 'gray')
                    .style('opacity', d => d.opacity)
                    .text(d => d.text)
                    .call(self.wordInteraction)

                }).start()
            } catch (e) {

            }
          })
        },
        async paintScatterplot() {
          const svg = d3.select('#overview-g')
          let margin_left = this.bubble.left
          let margin_top = 4
          let margin_right = this.bubble.top
          let margin_bottom = 4
          let width = this.bubble.width - margin_left - margin_right
          let height = this.bubble.height - margin_top - margin_bottom
          let data = this.scatterplot
          let self = this

          const disappear_time = 200
          const animation_time = 2000
          const glyph_margin = 25

          svg.append("clipPath")
            .attr("id", "clip_path")
            .append("rect")
            .attr('x', 0)
            .attr('y', 0)
            .attr('width', width)
            .attr('height', height)

          const main_g = svg
            .append('g')
            .attr('class', 'main_layer')
            .attr('transform', `translate(${margin_left}, ${margin_top})`)

          const word_g = svg
            .append('g')
            .attr('class', 'word_layer')
            .attr('transform', `translate(${margin_left}, ${margin_top})`)

          const label_g = svg
            .append('g')
            .attr('class', 'label_layer')
            .attr('transform', `translate(${margin_left}, ${margin_top})`)
            .style('font-family', 'sans-serif')
            .style('font-size', 12)

          // Here, I'm appending and positioning the y-axis label (Profit ($MM))
          label_g.append('g')
            .attr('transform', `translate(${3},${6})`)
            .append('text')
            //.attr('transform', 'rotate(90)')
            .text('Prediction Score')

          // Here, I'm appending and positioning the x-axis label (Revenue ($MM))
          /*
          label_g.append('text')
            .attr('x', width - 6)
            .attr('y', height)
            .attr('text-anchor', 'end')
            .text('Embedding t-SNE')
            */

          let xdomain = d3.extent(data.scatters, d => d.x)
          xdomain[0] = Math.floor(xdomain[0] * 20) / 20
          xdomain[1] = Math.ceil(xdomain[1] * 20) / 20
          let n_strips = Math.floor((xdomain[1] - xdomain[0]) / 0.05 + 1e-7)
          let focus_strip = null
          let ydomain = d3.extent(data.scatters, d => d.y)
          let grid_size = (width / n_strips / 4) * 0.5 / Math.sqrt(0.75)
          let grid_h = grid_size * Math.sqrt(0.75)

          let ticks = []
          let strips = []
          for (let i = 0; i < n_strips; ++i) {
            let left = xdomain[0] + i * (xdomain[1] - xdomain[0]) / n_strips
            let right = xdomain[0] + (i + 1) * (xdomain[1] - xdomain[0]) / n_strips
            ticks.push(left)
            let counts = [0, 0]
            data.scatters.filter(d => d.x >= left && d.x < right).forEach(d => {
              counts[d.label] = (counts[d.label] || 0) + 1
            })
            let p = 0
            if (counts[0] + counts[1] > 0) {
              p = (left < 0.5 - 1e-7 ? counts[1] : counts[0]) / (counts[0] + counts[1])
            }
            strips.push({ left, right, counts, weight: 1, index: i, is_top: left < 0.5 - 1e-7, p })
          }
          ticks.push(xdomain[1])

          let min_counts = Math.min(...strips.map(d => Math.min(d.counts[0], d.counts[1])))
          let max_counts = Math.max(...strips.map(d => Math.max(d.counts[0], d.counts[1])))
          let countScale = d3.scaleLinear([min_counts, max_counts], [0.1, 0.3])

          data.scatters.forEach(d => {
            if (d.x < 0.5 && d.label == 0 || d.x >= 0.5 && d.label == 1) {
              d.is_correct = true
            } else {
              d.is_correct = false
            }
          })

          let get_xrange = (width, strips) => {
            let tot_weight = 0
            for (let d of strips) tot_weight += d.weight
            let ret = [1]
            for (let i = 0; i < strips.length; ++i) ret.push(ret[i] - strips[i].weight / tot_weight)
            return ret.map(d => d * width)
          }

          let last_grids = null
          let last_keywords = []
          paintMainScatter()

          async function paintMainScatter() {
            let plotview_width = width - (glyph_margin + height / n_strips)
            let xrange = get_xrange(height, strips)
            let yrange = [5, plotview_width]
            let xScale = d3.scaleLinear(ticks, xrange)
            let yScale = d3.scaleLinear(ydomain, yrange)
            let yAxis = d3.axisLeft(xScale).tickValues(ticks).tickFormat(d => Number(d).toFixed(2))
            //let yAxis = d3.axisLeft(yScale)

            let rrange = [height / n_strips * 0.15, height / n_strips * 0.4]
            let rScale = d3.scaleSqrt(d3.extent(strips, d => d.counts[0] + d.counts[1]), rrange)
            let hex = hexbin().radius(grid_size).x(d => d.x).y(d => d.y)
            let plots = data.scatters.map((d, index) => ({ x: yScale(d.y), y: xScale(d.x), is_correct: d.is_correct, label: d.label, index }))
            let raw_grids = hex(plots)
            data.keywords.forEach(d => d.value = d.weight)
            raw_grids.forEach((d, index) => {
              d.count = 0
              d.error = 0
              //d.x += grid_h
              //d.y += grid_h
              if (d.length >= 1) {
                if (d[0].is_correct) {
                  d.color = self.labelColor[d[0].label]
                  d.error_color = self.labelColor[1 - d[0].label]
                } else {
                  d.color = self.labelColor[1 - d[0].label]
                  d.error_color = self.labelColor[d[0].label]
                }
              } else {
                d.color = 'gray'
              }
              for (let i = 0; i < d.length; ++i) {
                if (d[i].is_correct) {
                  d.count += 1
                } else {
                  d.error += 1
                }
              }
            })
            let currentGrids = raw_grids
            self.currentGridsData = currentGrids
            // console.log(currentGrids)
            let gridCountDomain = [0, 1, Math.max(...raw_grids.map(d => d.count))]
            let gridCountScale = d3.scaleLinear(gridCountDomain, [0, 0.3, 0.8])

            strips.forEach(d => {
              d.height = xScale(d.left) - xScale(d.right)
              d.r = rScale(d.counts[0] + d.counts[1])
            })

            let arc = d3.arc()
              .startAngle(d => -d.p * Math.PI)
              .endAngle(d =>  d.p * Math.PI)
              .innerRadius(d => 0)
              .outerRadius(d => rScale(d.counts[0] + d.counts[1]))

            main_g.selectAll('.strip')
              .data(strips)
              .join(
                enter => {
                  let g = enter
                    .append('g')
                    .attr('class', 'strip')
                    .attr('transform', d => `translate(0, ${xScale(d.right)})`)

                  g.append('rect')
                    .attr('width', width)
                    .attr('height', d => d.height)
                    .attr('fill', (d, i) => strips[i].is_top ? self.labelColor[0] : self.labelColor[1])
                    .style('stroke', 'white')
                    .style('stroke-width', 1)
                    .style('stroke-opacity', (d, i) => {
                      let value = 2 * countScale(strips[i].is_top ? d.counts[0] : d.counts[1])
                      return value > 0.25 ? 0 : value
                    })
                    .style('fill-opacity', (d, i) => countScale(strips[i].is_top ? d.counts[0] : d.counts[1]))
                    .on("dblclick", (d, i) => {
                      if (focus_strip == null) {
                        d.weight = 5
                        focus_strip = d
                      } else if (focus_strip.index == i) {
                        d.weight = 1
                        focus_strip = null
                      } else if (focus_strip != null) {
                        focus_strip.weight = 1
                        d.weight = 5
                        focus_strip = d
                      }
                      paintMainScatter()
                    })

                  let percent_g = g
                    .filter(d => d.counts[0] + d.counts[1] > 0)
                    .append('g')
                    .attr('class', 'percentage')
                    .attr('transform', (d, i) => `translate(${width - glyph_margin}, ${d.height / 2})`)

                  percent_g.append('circle')
                    .attr('r', d => d.r)
                    .attr('fill', (d, i) => d.counts[0] >= d.counts[1] ? self.labelColor[0] : self.labelColor[1])
                    .style('opacity', .5)
                    .on('click', (e) => {
                      let idxs = data.scatters.filter(d => d.x >= e.left && d.x < e.right && !d.is_correct).map(d => d.id)
                      bus.$emit('toggle_grids', idxs)
                    })

                  percent_g.append('path')
                    .attr('d', arc)
                    .attr('fill', (d, i) => d.counts[0] < d.counts[1] ? self.labelColor[0] : self.labelColor[1])
                    .style('opacity', .65)
                    .on('click', (e) => {
                      let idxs = data.scatters.filter(d => d.x >= e.left && d.x < e.right && !d.is_correct).map(d => d.id)
                      bus.$emit('toggle_grids', idxs)
                    })
                  return g
                },
                update => {
                  update
                    .transition().duration(animation_time)
                    .attr('transform', d => `translate(0, ${xScale(d.right)})`)

                  update.select('rect')
                    .transition().duration(animation_time)
                    .attr('height', d => d.height)

                  update.filter(d => d.counts[0] + d.counts[1] > 0)
                    .select('g.percentage')
                    .transition().duration(animation_time)
                    .attr('transform', (d, i) => `translate(${width - glyph_margin}, ${d.height / 2})`)
                }
              )

            main_g.selectAll('.grid')
              .data(currentGrids, d => Math.floor(d.y) * ~~plotview_width + Math.floor(d.x))
              .join(
                enter => {
                  let grid = enter
                    .append('g').attr('class', 'grid')
                    .style('opacity', 0)

                  grid.append('path')
                    .attr('class', 'hexagon')
                    //.attr("clip-path", "url(#clip_path)")
                    .attr("d", function (d) { return `M ${d.x} ${d.y} ${hex.hexagon()}`; })
                    .style('stroke', 'white')
                    .style('stroke-width', 1)
                    .style('fill', d => d.color)
                    .style('fill-opacity', d => gridCountScale(d.count))

                  grid.append('path')
                    .attr('class', 'cross')
                    .attr('transform', d => `translate(${d.x},${d.y})`)
                    .attr('d', `M -3 -3 L 3 3 M 3 -3 L -3 3`)
                    .style('stroke', d => d.error_color)
                    .style('stroke-width', 2.5)
                    .style('opacity', d => d.error ? 0.7 : 0)

                  let hover_grid_item = null
                  grid.on('mouseover', function (d) {
                    hover_grid_item = d
                    d3.select(this).append('path')
                      .attr('class', 'hexagon_outline')
                      .attr("d", function (d) { return `M ${d.x} ${d.y} ${hex.hexagon()}`; })
                      .style('stroke', 'orange')
                      .style('stroke-width', 2)
                      .style('fill', 'none')
                    let text = ''
                    if (d.count && d.error) {
                      text = `${d.count} correct samples and ${d.error} wrong samples`
                    } else if (d.count) {
                      text = `${d.count} correct samples`
                    } else {
                      text = `${d.error} wrong samples`
                    }
                    text = `<p>${text}</p>`
                    let left = (d3.event.pageX + 10)
                    let top = (d3.event.pageY - 10)
                    self.showTooltip({ top, left, content: text })

                    const show_detail = async () => {
                      let resp = await self.getSamples(d.map(e => e.index))
                      text = text + resp.slice(0, 5).map((e, index) => `#${index + 1}: ${e.text}`).join('</br>')

                      self.showTooltip({ top, left, content: text })
                    }
                    setTimeout(() => {
                      if (hover_grid_item == d) {
                        show_detail()
                      }
                    }, 500)
                  }).on('mouseout', function (d) {
                    hover_grid_item = null
                    d3.select(this).select('path.hexagon_outline').remove()
                    self.hideTooltip()
                  }).on('click', function(d) {
                    bus.$emit('toggle_grids', d.map(e => e.index))
                  })

                  grid.transition().duration(animation_time)
                    .style('opacity', 1)
                },
                update => {
                  update
                    .select('path.hexagon')
                    .transition().duration(animation_time)
                    .attr("d", function (d) { return `M ${d.x} ${d.y} ${hex.hexagon()}`; })
                    .style('fill', d => d.color)
                    .style('fill-opacity', d => gridCountScale(d.count))

                  update
                    .select('path.cross')
                    .transition().duration(animation_time)
                    .attr('transform', d => `translate(${d.x},${d.y})`)
                    .style('stroke', d => d.error_color)
                    .style('opacity', d => d.error ? 0.7 : 0)
                },
                exit => {
                  exit.transition().duration(animation_time)
                    .style('opacity', 0)
                    .remove()
                }
              )

            let grids = main_g.selectAll('.grid')
            self.currentGrids = grids

            let lasso_start = () => {
              //console.log('start')
            };

            let lasttime = 0
            let lasso_draw = () => {
              if (new Date() - lasttime <= 100) {
                return
              }
              lasttime = new Date()
              current_lasso.possibleItems()
                .style('opacity', 1.0)


              if (current_lasso.possibleItems().nodes().length > 0) {
                current_lasso.notPossibleItems()
                    .style('opacity', .4)
              } else {
                current_lasso.notPossibleItems()
                  .style('opacity', 1)
              }
            };

            let lasso_end = () => {
              if (current_lasso.selectedItems().nodes().length > 0) {
                current_lasso.notSelectedItems()
                  .style('stroke', .4)
              } else {
                current_lasso.notSelectedItems()
                  .style('stroke', 1)
              }
              current_lasso.selectedItems()
                .style('opacity', 1)

              let grids_ = current_lasso.selectedItems().data()
              let idxs = [].concat(...grids_.map(d => d.map(e => e.index)))
              if (idxs.length > 0)
                self.refreshSelection(idxs, grids_)
            };

            const current_lasso = lasso()
              .closePathDistance(305)
              .closePathSelect(true)
              .targetArea(main_g)
              .items(grids)
              .on("start", lasso_start)
              .on("draw", lasso_draw)
              .on("end", lasso_end)
            self.lasso = current_lasso

            main_g.select('g.grid-lasso').remove()
            main_g
              .append('g')
              .attr('class', 'grid-lasso')
              //.attr('transform', `translate(${0},${0})`)
              .call(current_lasso)

            main_g.select('g.x-axis').remove()

            main_g
              .append('g')
              .attr('class', 'x-axis')
              .attr('transform', `translate(${0},${0})`)
              .call(yAxis)
              // remove the line between the ticks and the chart
              .select('.domain').remove()

            let keywords = data.keywords
            window.keywords = keywords
            keywords = keywords.slice(0, 200)
            keywords = JSON.parse(JSON.stringify(keywords))
            let valueRange = d3.extent(keywords, d => d.value)
            let pwords = keywords.filter(d => d.score.mean > 0.5).sort((a, b) => b.value - a.value)
            let nwords = keywords.filter(d => d.score.mean <= 0.5).sort((a, b) => b.value - a.value)
            pwords.forEach((d, rank) => d.rank = 1.0 / (rank ** 1.15 * 0.1 + 1))
            nwords.forEach((d, rank) => d.rank = 1.0 / (rank ** 1.15 * 0.1 + 1))
            keywords = pwords.concat(nwords)
            let sizeScale = d3.scaleLinear(d3.extent(keywords, d => d.rank), [12, 40])
            keywords.forEach(d => d.size = sizeScale(d.rank))
            // console.log(JSON.parse(JSON.stringify(keywords)))

            //word_g.selectAll('.keyword').remove()
            let barriers = []

            function add_barriers(top, bottom) {
              let filtered_grids = currentGrids.filter(d => d && d.y >= top && d.y < bottom)
              filtered_grids = filtered_grids.sort((a, b) => a.x - b.x)
              if (filtered_grids.length == 0) return
              let last = filtered_grids[0].x
              for (let j = 1; j <= filtered_grids.length; ++j) {
                if (j != filtered_grids.length && filtered_grids[j].x - filtered_grids[j - 1].x <= grid_size * 30) {
                  continue
                } else {
                  let x1 = filtered_grids[j - 1].x + grid_size
                  if (x1 + grid_size * 10 > plotview_width) {
                    x1 = plotview_width
                  }
                  barriers.push({
                    x0: last - grid_size - 5,
                    x1: x1 + 5,
                    y0: top - 5,
                    y1: bottom + 5,
                  })
                  if (j != filtered_grids.length) {
                    last = filtered_grids[j].x
                  }
                }
              }
            }

            for (let i = 0; i < n_strips; ++i) {
              let top = xScale(strips[i].right)
              let bottom = xScale(strips[i].left)
              if (strips[i].weight > 1) {
                let step = (bottom - top) / 3
                for (let k = 0; k < 3; ++k) {
                  add_barriers(top + k * step, top + (k + 1) * step)
                }
              } else {
                add_barriers(top, bottom)
              }
              barriers.push({
                x0: i * 2 >= n_strips ? 0 : plotview_width * 0.7,
                x1: i * 2 >= n_strips ? plotview_width * 0.3 : plotview_width,
                y0: top,
                y1: bottom,
              })
              /*
              barriers.push({
                x0: 0,
                x1: plotview_width,
                y0: bottom - 1,
                y1: bottom + 1,
              })
              */
            }
            barriers.push({
              x0: plotview_width - 40,
              x1: plotview_width,
              y0: height - 15,
              y1: height,
            })
            barriers.push({
              x0: 0,
              x1: plotview_width,
              y0: 0,
              y1: 20,
            })
            barriers.push({
              x0: 0,
              x1: plotview_width,
              y0: height - 20,
              y1: height,
            })
            barriers.push({
              x0: 0,
              x1: 10,
              y0: 0,
              y1: 100,
            })
            // barriers = barriers.filter(d => d.x1 - d.x0 > 15)
            let dict = {}
            last_keywords.forEach((d, i) => {
              dict[d.word] = i
              d.is_new = false
            })
            keywords.splice(0, 0, JSON.parse(JSON.stringify(keywords[0])))
            d3_wordcloud().size([plotview_width, height])
              .words(keywords)
              .text(d => d.word)
              .barriers(barriers)
              .fromCenter(false)
              .xrange(d => {
                if (dict[d.word]) {
                  let mid = last_keywords[dict[d.word]].x / plotview_width
                  let left = mid - 0.1
                  let right = mid + 0.1
                  return [Math.max(0, left), Math.min(right, 1)]
                } else {
                  return [0, 1]
                }
              })
              /*
              .xrange(d => {
                let left = yScale(d.embedding.mean - d.embedding.std) / plotview_width
                let right = yScale(d.embedding.mean + d.embedding.std) / plotview_width
                let mid = yScale(d.embedding.mean) / plotview_width
                let alpha = 0
                if (d.score.mean < 0.47) alpha = -0.4
                if (d.score.mean > 0.53) alpha = 0.4
                return [Math.max(0, left + alpha), Math.min(1, right + alpha), mid]
              })*/
              .yrange(d => {
                if (dict[d.word]) {
                  let mid = last_keywords[dict[d.word]].y / height
                  let left = mid - 0.15
                  let right = mid + 0.15
                  return [Math.max(0, left), Math.min(right, 1), mid]
                } else {
                  let alpha = 1, beta = 1
                  if (d.score.mean < 0.47) alpha = .5, beta = 2
                  if (d.score.mean > 0.53) alpha = 2, beta = .5
                  let std = Math.max(0.05, d.score.std)
                  let left = xScale(d.score.mean + std * alpha) / height
                  let right = xScale(d.score.mean - std * beta) / height
                  let mid = xScale(d.score.mean) / height
                  left = Math.floor(left * 10) / 10
                  right = Math.ceil(right * 10) / 10
                  if (left < 0.5) mid = left
                  else if (right > 0.5) mid = right
                  return [Math.max(0, left), Math.min(1, right), mid]
                }
              })
              .fontSize(d => d.size)
              .font('sans-serif')
              .fontWeight(d => sizeScale(d.value) >= 0 ? 'bold' : 'normal')
              .on('end', (words) => {
                // console.log(words)
                let all_words = words.filter(d => d.placed)
                  .map(d => ({
                    x: d.x,
                    y: d.y,
                    layer: 0,
                    size: d.size,
                    text: d.text,
                    width: d.w,
                    weight: 'bold',
                    highlight: d.highlight,
                    fill: d.score.mean < 0.44 ? self.negativeColor : (d.score.mean > 0.56 ? self.positiveColor : 'gray')
                  }))
                self.overviewWords = all_words
              }).start()
          }
        },
        async paintLinechart(highlight_word = null) {
          await paintLineChart(this, highlight_word)
        },
        async selectThumbnail(index) {
          this.current = this.thumbnails[index]
          let resp = await axios.post(`${this.server_url}/api/layers`, { idxs: this.current.idxs, attrs: this.word_attrs  })
          this.setLayers(resp.data)
          this.paintLinechart()
          this.brushGrid(this.current.idxs)
          this.selectedThumbnail = index
        },
        async clearThumbnail() {
          await this.selectThumbnail(0)
          this.thumbnails = this.thumbnails.slice(0, 1)
        },
        saveWordAttr() {
          this.enable_word_attr = false
          this.refreshLinechart()
        },
        async refreshLinechart() {
          let resp = await axios.post(`${this.server_url}/api/layers`, { idxs: this.current && this.current.idxs || null, attrs: this.word_attrs })
          this.setLayers(resp.data)
          this.paintLinechart()
        },
        async refreshSelection(idxs, grids = null) {
          let self = this
          let resp = await axios.post(`${this.server_url}/api/layers`, { idxs, attrs: this.word_attrs })
          this.setLayers(resp.data)
          this.current = {}
          resp = await self.getSamples(idxs)
          this.current_items = resp.sort((a, b) => a.score - b.score)
          this.current.grids = grids
          this.current.idxs = idxs
          this.paintLinechart()
          this.brushGrid(idxs)
          this.thumbnails.push(this.current)
          this.selectedThumbnail = this.thumbnails.length - 1
        },
        async removeDAG(index) {
          this.DAG_tabs.splice(index, 1)
        },
        async selectDAG(item) {
          for (let i = 0; i < this.DAG_tabs.length; ++i) {
            this.DAG_tabs[i].current = false
          }
          item.current = true
          this.refreshDAG(item.type, item.idx)
        },
        async addSentenceDAG(index) {
          for (let i = 0; i < this.DAG_tabs.length; ++i) {
            this.DAG_tabs[i].current = false
          }
          this.DAG_tabs.push({
            'type': 'sentence',
            'idx': index,
            'current': true,
          })
          await this.refreshDAG('sentence', index)
          /*
          let retained_words = []
          let discarded_words = []
          for (let d of this.layout.lines) {
            if (!(d.text.length > 1 || d.text.length == 1 && isalpha(d.text))) {
              continue
            }
            let flag = 1
            let max_contri = 0
            let k = 2
            for (let i = 0; i < d.line.length; ++i) {
              if (!d.line[i].display) {
                flag = 0
                discarded_words[i] = discarded_words[i] || []
                discarded_words[i].push([d.text, 0])
                break
              }
              if (i >= 2 && Math.abs(d.line[i].contri) > max_contri) {
                max_contri = Math.abs(d.line[i].contri)
                k = i
              }
            }
            if (!flag) continue
            retained_words[k] = retained_words[k] || []
            retained_words[k].push([d.text, d.line[k].contri < 0 ? 0.6 : 0.4])
          }
          console.log(this.layout)
          */
          await this.paintLinechart()//{ retained_words, discarded_words })
        },
        async addWordDAG(word) {
          for (let i = 0; i < this.DAG_tabs.length; ++i) {
            this.DAG_tabs[i].current = false
          }
          this.DAG_tabs.push({
            'type': 'word',
            'idx': word,
            'current': true,
          })
          this.refreshDAG('word', word)
        },
        async refreshDAG(type, idx) {
          let req = { level: type, layers: this.showed_layers }
          if (type == 'sentence') {
            req.idx = idx
          } else {
            req.word = idx
          }
          this.setViewtype(type)
          let resp = await axios.post(`${this.server_url}/api/networks`, req)
          if (type == 'sentence') {
            this.current_text = this.getSample(idx).text
            console.log('this.current_text', this.current_text)
            this.setLayers(resp.data.linechart)
          }
          this.setNetwork(resp)
          this.calcDAG()
          this.paintDAG()
        },
        paintDAG() {
          if (this.current_viewtype == 'word') {
            paintWordDAG(this)
            this.paintWordcloud()
          } else if (this.current_viewtype == 'sentence') {
            paintSentenceDAG(this)
          }
        },
      },
      async mounted() {
        this.svgResize()
        document.getElementsByClassName('lds-facebook')[0].style.display = 'none'
//        await this.addSentenceDAG(113)
        let resp = await axios.post(`${this.server_url}/api/scatterplot`, {})
        await this.set_scatterplot(resp)
        await this.paintScatterplot()
        await this.refreshSelection(null)
        window.onresize = () => {
          this.svgResize()
        }
        await this.fetchAllSample()
        bus.$on('add_word_DAG', (word) => this.addWordDAG(word))
        bus.$on('add_sentence_DAG', (idx) => this.addSentenceDAG(idx))
        bus.$on('highlight_grid', (idxs) => this.highlightGrid(idxs))
        bus.$on('brush_grid', (idxs) => this.brushGrid(idxs))
        bus.$on('toggle_grid', (idxs) => this.toggleGrid(idxs))
      }
};
</script>

<style>
.lds-facebook {
  display: inline-block;
  position: relative;
  z-index: 0;
  width: 80px;
  height: 80px;
  left: 45vw;
  top: 45vh;
}

#app {
  z-index: 1;
}

.lds-facebook div {
  display: inline-block;
  position: absolute;
  left: 8px;
  width: 16px;
  background: #555;
  animation: lds-facebook 1.2s cubic-bezier(0, 0.5, 0.5, 1) infinite;
}
.lds-facebook div:nth-child(1) {
  left: 8px;
  animation-delay: -0.24s;
}
.lds-facebook div:nth-child(2) {
  left: 32px;
  animation-delay: -0.12s;
}
.lds-facebook div:nth-child(3) {
  left: 56px;
  animation-delay: 0;
}
@keyframes lds-facebook {
  0% {
    top: 8px;
    height: 64px;
  }
  50%, 100% {
    top: 24px;
    height: 32px;
  }
}

#network-svg {
  -webkit-transition: opacity 1s ease-in-out;
  -moz-transition: opacity 1s ease-in-out;
  -o-transition: opacity 1s ease-in-out;
  transition: opacity 1s ease-in-out;
}

.core-view {
  height: 100%;
  background-color: #dddddd;
}

.max-height {
  height: 100%;
}

.my-subtitle {
  font-size: 15px;
  color: rgba(0, 0, 0, 0.6)
}

.corpus-view {
  background: #fff;
  box-shadow: 0 2px 4px rgba(26, 26, 26, .3);
}

.network-view {
  background: #fff;
  box-shadow: 0 2px 4px rgba(26, 26, 26, .3);
}

.lasso path {
  stroke: gray;
  stroke-width: 2px;
}

.lasso .drawn {
  fill-opacity: .05;
}

.lasso .loop_close {
  fill: none;
  stroke-dasharray: 4, 4;
}

.lasso .origin {
  fill: #3399FF;
  fill-opacity: .5;
}

.svgview {
  width: 100%;
  height: 100%;
}
</style>