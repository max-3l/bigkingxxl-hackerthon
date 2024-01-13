<template>
  <q-form @submit="onSubmit" v-show="showInput" class="input">
    <q-input rounded outlined v-model="text" label="Prompt" />
  </q-form>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
} from 'vue';


export default defineComponent({
  name: 'ExampleComponent',
  props: {
    title: {
      type: String,
      required: true
    },
    active: {
      type: Boolean
    }
  },
  setup() {
    return {
      text: ref(''),
      showInput: ref(true)
    };
  },

  methods: {
    onSubmit() {
      console.log(this.text);
      this.showInput = false;
    }
  }
});
</script>

<style>
.input {
  width: 90%
}
</style>
