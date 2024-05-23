<script setup>
import { Codemirror } from 'vue-codemirror'
import { javascript } from '@codemirror/lang-javascript'
import { cpp } from '@codemirror/lang-cpp'
import { oneDark } from '@codemirror/theme-one-dark'
import { computed, shallowRef, watch } from 'vue'
import { python } from '@codemirror/lang-python'
import { java } from '@codemirror/lang-java'


const props = defineProps({
  code: {
    type: String,
    default: ''
  },
  onCodeChanged: {
    type: Function,
    default: () => {
    }
  },
  currentLanguage: {
    type: String,
    default: ''
  }
})

const languageSDK = {
  '62': java(),
  '63': javascript(),
  '71': python(),
}

const extensions = computed(() => {
  return [languageSDK[props.currentLanguage], oneDark]
})

const view = shallowRef()
const handleReady = (payload) => {
  view.value = payload.view
}
</script>

<template>
  <Codemirror
    :autofocus="true"
    :extensions="extensions"
    :indent-with-tab="true"
    :model-value="props.code"
    :style="{ height: '100%' }"
    :tab-size="2"
    class="rounded-md"
    placeholder="Write your code here"
    @change="props.onCodeChanged"
    @ready="handleReady"
  />
</template>