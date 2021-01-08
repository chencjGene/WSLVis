<template>
  <div class="text-div" 
    @click="click"
    >
    {{ text }}</div>
</template>


<script>
import { mapState, mapMutations } from "vuex";
export default {
  name: "TextItem",
  props: {
    text: {
      type: String,
      default: "test"
    },
    id: {
      type: Number,
      default: -1
    }
  },
  computed: {
    ...mapState(["focus_text"])
  },
  data: () => ({}),
  methods: {
    ...mapMutations(["set_focus_text"]),
    click(){
      console.log("text item click");
      this.set_focus_text(this.id);
    },
  }
};
</script>

<style scoped>
.text-div{
  cursor: pointer;
  font-size: 16px;
  margin-left: 8px;
  margin-right: 8px;
  padding-top: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #ddd;
  word-break: break-all;
}
.text-div:hover {
  background: #ddd;
}
</style>