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
  '4': cpp(),
  '5': cpp(),
  '6': cpp(),
  '7': cpp(),
  '8': cpp(),
  '9': cpp(),
  '10': cpp(),
  '11': cpp(),
  '12': cpp(),
  '13': cpp(),
  '14': cpp(),
  '15': cpp(),
  '26': java(),
  '27': java(),
  '28': java(),
  '29': javascript(),
  '30': javascript(),
  '34': python(),
  '35': python(),
  '36': python(),
  '37': python()
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
    :on-change="props.onCodeChanged"
    :style="{ height: '100%' }"
    :tab-size="2"
    class="rounded-md"
    placeholder="Write your code here"
    @ready="handleReady"
  />
</template>