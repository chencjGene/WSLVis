<template>
  <div class="text-div" 
    @click="click"
    >
    {{ text }}</div>
</template>


<script>
import { mapState, mapMutations, mapActions } from "vuex";
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
    ...mapState([])
  },
  data: () => ({}),
  methods: {
    ...mapActions(["fetch_single_image_detection_for_focus_text"]),
    ...mapMutations([]),
    click(){
      console.log("text item click");
      this.fetch_single_image_detection_for_focus_text({
        image_id: this.id
      });
      // this.set_focus_text(data);
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