<template>
  <g class="word-group">
    <rect v-if="hover_item"
      :x="hover_item.x"
      :y="hover_item.y - hover_item.size + 2"
      class="word-hover-item"
      key="new rect"
      :height="hover_item.size"
      :width="hover_item.width"
      :style = "{
        'fill' : hover_item.fill,
        'fill-opacity' : 0.3,
        'stroke' : hover_item.fill,
        'stroke-width' : '1px',
      }"
    >
    </rect>
    <transition-group mode="out-in"
      name="word-list" tag="g">
      <template v-if="interaction == 'filter'">
        <rect v-for="item in selected_items"
          :x="item.x"
          :y="item.y - item.size + 2"
          class="word-list-item"
          :key="`${item.key}bg`"
          :height="item.size"
          :width="item.width"
          :style = "{
            'fill' : item.fill,
            'fill-opacity' : 0.15,
            'stroke' : item.fill,
            'stroke-width' : '1px',
          }">
        </rect>
      </template>
      <text v-for="item in items"
        class="word-list-item"
        :x="item.x"
        :y="item.y"
        :font-size="item.size"
        :font-weight="item.weight"
        :key="item.key"
        @mouseenter="onMouseOver(item)"
        @mouseout="onMouseOut(item)"
        @click="onClick(item)"
        :class="{
          'highlight':  !highlight || highlight_text.indexOf(item.text) != -1,
        }"
        :style = "{
          'fill': item.fill,
        }"
      >
        {{ item.text }}
      </text>
    </transition-group>
  </g>
</template>

<script>
import { mapGetters, mapMutations, mapActions, mapState } from 'vuex'
import bus from '../plugins/bus'

const sleep = (timeout) => new Promise((resolve) => {
  setTimeout(resolve, timeout);
})

const isalpha = val => /^[a-zA-Z]+$/.test(val)
const islegal = val => isalpha(val) && val.length > 1 && val.indexOf('_') == -1

export default {
  data: function() {
    return {
      hover_item: null,
      hover_set: new Set(),
    }
  },
  computed: {
    ...mapState([ 'filtered_words' ]),
    ...mapGetters([ 'getWordIdxs', 'getSamples' ]),
    items() {
      let cnt = {}
      console.log(this.data)
      return this.data.map(d => {
        cnt[d.text] = (cnt[d.text] || 0) + 1
        return {
          x: d.x,
          y: d.y,
          size: d.size,
          width: d.width,
          weight: d.weight,
          text: d.text,
          key: `${d.text}${d.layer}`,
          fill: d.fill,
          // hover: false,
        }
      }).filter(d => islegal(d.text))
    },
    selected_items() {
      const filter_set = new Set(this.filtered_words)
      return this.items.filter(d => filter_set.has(d.text))
    }
  },
  watch: {
  },
  props: {
    data: Array,
    tooltip: {
      type: Boolean,
      default: false,
    },
    interaction: {
      type: String,
      default: 'DAG',
    },
    highlight: {
      type: Boolean,
      default: false,
    },
    highlight_text: {
      type: String,
      default: '',
    },
  },
  methods: {
    ...mapActions([ 'fetchWordIndex' ]),
    ...mapMutations([ 'changeFilteredWord', 'showTooltip', 'hideTooltip' ]),
    async onMouseOver(d) {
      const left = window.event.pageX
      const top = window.event.pageY
      this.hover_item = d
      this.hover_set.add(d.key)
      await sleep(300)
      if (this.hover_item != d) {
        return
      }
      await this.fetchWordIndex(d.text)
      let idxs = this.getWordIdxs(d.text)
      bus.$emit('highlight_grid', idxs)
      let text = `<p>${d.text}, ${idxs.length} samples </p>`
      let resp = await this.getSamples(idxs)
      text = text + resp.slice(0, 8).map((e, index) => `#${e.index}: ${e.text}`).join('</br>')
      if (this.tooltip) {
        this.showTooltip({ top, left, content: text })
        await sleep(5000)
        this.hover_item = null
        this.hideTooltip()
      }
    },
    async onMouseOut(d) {
      // d.hover = false
      await sleep(300)
      this.hover_set.delete(d.key)
      if (this.hover_set.size == 0) {
        bus.$emit('highlight_grid', null)
        this.hover_item = null
        if (this.tooltip) {
          this.hideTooltip()
        }
      }
    },
    async onClick(d) {
      if (this.interaction == 'filter') {
        this.changeFilteredWord(d.text)
      } else if (this.interaction == 'DAG') {
        await this.fetchWordIndex(d.text)
        let idxs = this.getWordIdxs(d.text)
        if (idxs.length > 10) {
          bus.$emit('add_word_DAG', d.text)
        }
      }
    },
  }
}
</script>
<style scoped>
.word-hover-item {
  transition: opacity 1s;
}
.word-list-item {
  opacity: 1;
}
.word-list-item {
  transition: all 1s;
}
.word-list-enter {
  transition-delay: 1s;
  opacity: 0;
}
.word-list-leave-to {
  opacity: 0;
}
</style>