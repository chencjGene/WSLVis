<template>
  <div class="text-div" >{{ text }}</div>
</template>


<script>
export default {
  name: "TextItem",
  props: {
    text: {
      type: String,
      default: "test"
    }
  },
  data: () => ({}),
  methods: {
    click(){
      console.log("text item click");
    }
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
</style>