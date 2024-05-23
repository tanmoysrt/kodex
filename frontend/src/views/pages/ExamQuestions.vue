<script setup>

import { useExam } from '@/store/exam'
import { Button, FormControl, Select } from 'frappe-ui'
import { computed, ref } from 'vue'
import MarkdownRenderer from '@/views/components/MarkdownRenderer.vue'
import CodeEditor from '@/views/partials/CodeEditor.vue'
import TestCase from '@/views/partials/TestCase.vue'

const examStore = useExam()
const questionPanelWidthPercentage = ref(50)
const answerPanelWidthPercentage = computed(() => 100 - questionPanelWidthPercentage.value)
const resizerBusy = ref(false)

const resizeTabs = (e) => {
  e.preventDefault()
  const element = document.getElementById('exam-questions-container')
  const startX = element.getBoundingClientRect().x
  const endX = element.getBoundingClientRect().x + element.getBoundingClientRect().width
  if (e.clientX > endX || e.clientX < startX) {
    return false
  }
  const relativeX = e.clientX - startX
  const newQuestionPanelWidthPercentage = relativeX / element.getBoundingClientRect().width * 100
  if (newQuestionPanelWidthPercentage > 25 && newQuestionPanelWidthPercentage < 75) {
    questionPanelWidthPercentage.value = newQuestionPanelWidthPercentage
  }
}

const onSelectResizer = () => {
  if (resizerBusy.value) return
  resizerBusy.value = true
  document.addEventListener('mousemove', resizeTabs)
  document.addEventListener('mouseup', (e) => {
    document.removeEventListener('mousemove', resizeTabs)
    resizerBusy.value = false
  })
}
</script>

<template>
  <div class="flex flex-col h-screen max-h-screen p-6">
    <!--  Top bar  -->
    <div class="flex flex-row items-center justify-between">
      <div class="text-2xl font-bold">{{ examStore.details_resource.data.exam.title }}</div>
      <div class="flex flex-row items-center gap-5">
        <p class="text-[1.8rem] font-bold">{{ examStore.time_left }}</p>
        <Button theme="green" variant="solid">
          Submit Exam
        </Button>
      </div>
    </div>
    <!--  Content  -->
    <div class="flex flex-row h-full gap-4 mt-5">
      <div id="exam-questions-container" class="flex flex-row w-full h-full gap-2">
        <div :style="`width: ${questionPanelWidthPercentage}%`" class="h-full p-4 border-2 rounded-md">
          <MarkdownRenderer :source="examStore.current_question.description" />
        </div>
        <div class="w-[5px] bg-gray-400 h-full rounded-md cursor-col-resize hover:bg-gray-500 focus:bg-gray-500"
          @mousedown="onSelectResizer"></div>
        <div :style="`width: ${answerPanelWidthPercentage}%`" class="h-full p-4 border-2 rounded-md">
          <!--     Answers Panel   -->
          <!--    Text question      -->
          <div v-if="examStore.current_question.type === 'text'">
            <p class="mb-3 font-medium text-black">Write down the answer here.</p>
            <FormControl :disabled="false" label="" placeholder="Placeholder" rows="30" size="lg" type="textarea"
              variant="outline" :value="examStore.get_current_question_answer"
              @input="(e) => examStore.temp_store_answer(e.target.value)" />
            <div v-if="examStore.current_question" class="flex justify-end w-full gap-2 mt-2">
              <Button theme="gray" variant="solid" @click="examStore.submit_answer"
                :loading="examStore.is_answer_submitting">
                Submit & Proceed to Next
              </Button>
            </div>
          </div>
          <!--    Multiple choice question      -->
          <div v-else-if="examStore.current_question.type === 'mcq'">
            <p class="mb-3 font-medium text-black">Select the correct answer</p>
            <div class="flex flex-col gap-3">
              <div v-for="(option, index) in examStore.current_question.mcq_question_choices" :key="index" :class="{
                'border-black': examStore.get_current_question_answer === option,
              }" class="px-4 py-2 transition-all border-2 rounded-md cursor-pointer hover:ring-1 ring-gray-400"
                @click="examStore.temp_store_answer(option)">
                {{ option }}
              </div>
            </div>
            <div class="flex justify-end w-full gap-2 mt-5">
              <Button theme="gray" variant="solid" @click="examStore.submit_answer"
                :loading="examStore.is_answer_submitting">
                Submit & Proceed to Next
              </Button>
            </div>
          </div>
          <!--      Code question      -->
          <div v-else-if="examStore.current_question.type === 'coding'" class="flex flex-col h-full">
            <!--     Language Switcher       -->
            <div class="flex flex-row justify-end w-full mb-2">
              <p class="mr-3 font-medium">Language</p>
              <Select :options="examStore.available_languages.map((x) => ({ label: x.title, value: x.id }))"
                :value="examStore.current_language" variant="outline" @change="examStore.switch_language"></Select>
            </div>
            <CodeEditor :code="examStore.get_current_question_answer" :current-language="examStore.current_language"
              :on-code-changed="(code) => examStore.temp_store_answer(code)" />
            <div class="flex flex-wrap w-full gap-2 mt-2">
              <TestCase v-for="(_, index) in examStore.current_question.coding_question.test_cases" :key="index"
                :index="index" />
            </div>
            <div class="flex flex-row justify-end my-2">
              <Button icon-left="play" theme="gray" variant="outline" @click="examStore.run_all_test_cases">
                Run All Codes
              </Button>
              <Button theme="gray" variant="solid" @click="examStore.submit_answer" class="ml-2"
                :loading="examStore.is_answer_submitting">
                Submit & Proceed to Next
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!--  Question Switcher  -->
    <div class="flex flex-row items-center justify-center w-full max-w-full gap-3 py-1 mt-4 overflow-hidden">
      <Button icon-left="arrow-left" variant="outline" @click="examStore.previous_question"
        :disabled="!examStore.previous_question_button_enbaled">Previous</Button>
      <div v-for="(_, index) in examStore.question_series" :key="index" :class="{
        '!border-2 border-black': examStore.current_question_index === index,
        '!border-2 border-green-500': examStore.answers[examStore.question_series[index]] !== undefined && examStore.current_question_index !== index
      }"
        class="flex items-center justify-center h-full text-base transition-all border rounded-sm cursor-pointer aspect-square"
        @click="examStore.switch_question(index)">
        {{ index + 1 }}
      </div>
      <Button icon-right="arrow-right" variant="outline" @click="examStore.next_question"
        :disabled="!examStore.next_question_button_enabled">Next</Button>
    </div>
  </div>
</template>

<style scoped></style>