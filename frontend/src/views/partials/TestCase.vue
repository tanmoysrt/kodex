<script setup>

import { Button, Dialog } from 'frappe-ui'
import { computed, ref } from 'vue'
import { useExam } from '@/store/exam'

const props = defineProps({
  index: Number
})

const examStore = useExam()
const testcase = computed(() => examStore.current_question.coding_question.test_cases[props.index])
const status = computed(() => {
  if (testcase.value.name in examStore.test_cases_result_status) {
    return examStore.test_cases_result_status[testcase.value.name]
  }
  return -1
})
const isDetailsDialogOpen = ref(false)
const test_case_result = computed(() => {
  return examStore.test_cases_result[testcase.value.name]
})
const isCorrectOutput = computed(() => {
  return status.value === 1 ? testcase.value?.output === test_case_result.value?.output : false;
})

</script>

<template>
  <div :class="{
    'border-green-500': status !== -1 && status !== 2 && isCorrectOutput,
    'border-red-500': status !== -1 && status !== 2 && !isCorrectOutput,
  }" class="flex flex-row items-center justify-between py-1 pl-2 pr-1 border-2 rounded-md w-60">
    <p class="text-sm">Test Case {{ props.index + 1 }}</p>
    <div class="flex flex-row gap-2">
      <Button icon="code" theme="gray" variant="outline" @click="isDetailsDialogOpen = true"></Button>
      <Button :loading="status === 2" icon="play" theme="gray" variant="outline"
        @click="examStore.test_code(props.index)"></Button>
    </div>
  </div>
  <!-- Dialog to show details -->
  <Dialog v-model="isDetailsDialogOpen">
    <template #body-title>
      <p class="font-medium">Testcase Details</p>
    </template>
    <template #body-content>
      <div class="flex flex-col gap-1">
        <p class="font-medium">Input</p>
        <div class="px-2 py-1 rounded-md select-none bg-gray-50">
          {{ testcase?.input }}
        </div>
        <p class="mt-2 font-medium">Expected Output</p>
        <div class="px-2 py-1 rounded-md select-none bg-gray-50">
          {{ testcase?.output }}
        </div>
        <div class="w-full h-0.5 my-2 bg-black rounded-md" v-if="status === 0 || status === 1"></div>
        <div class="flex flex-col w-full gap-1" v-if="status === 0 || status === 1">
          <div class="flex flex-row w-full gap-2">
            <div class="w-full">
              <p class="font-medium ">Status</p>
              <div class="px-2 py-1 font-bold rounded-md select-none bg-gray-50" :class="{
                'text-green-500': isCorrectOutput,
                'text-red-500': !isCorrectOutput
              }">
                {{ isCorrectOutput ? "Correct" : "Failed" }}
              </div>
            </div>
            <div class="w-full">
              <p class="font-medium ">Memory (KB)</p>
              <div class="px-2 py-1 rounded-md select-none bg-gray-50">
                {{ test_case_result?.memory_kb }}
              </div>
            </div>
            <div class="w-full">
              <p class="font-medium ">Time</p>
              <div class="px-2 py-1 rounded-md select-none bg-gray-50">
                {{ test_case_result?.time_second }} KB
              </div>
            </div>
          </div>
          <p class="mt-2 font-medium" v-if="status === 1">Output</p>
          <div class="px-2 py-1 rounded-md select-none bg-gray-50" v-if="status === 1"
            v-html="test_case_result?.output === '' ? 'No Output' : test_case_result?.output">
          </div>
          <p class="mt-2 font-medium">Compile Output</p>
          <div class="px-2 py-1 rounded-md select-none bg-gray-50"
            v-html="test_case_result?.compile_output === '' ? 'No Output' : test_case_result?.compile_output">
          </div>
          <p class="mt-2 font-medium" v-if="status === 0">Error</p>
          <div class="px-2 py-1 rounded-md select-none bg-gray-50" v-if="status === 0"
            v-html="test_case_result?.error === '' ? 'No logs' : test_case_result?.error">
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex flex-row justify-end w-full gap-2">
        <Button @click="isDetailsDialogOpen = false">
          Close
        </Button>
        <Button :loading="status === 2" theme="gray" variant="outline" @click="examStore.test_code(props.index)"
          iconLeft="play">Run
          Code</Button>
      </div>
    </template>
  </Dialog>
</template>

<style scoped></style>