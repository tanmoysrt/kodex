<script setup>

import { useExam } from '@/store/exam'
import { Button, FormControl } from 'frappe-ui'
import { computed, ref } from 'vue'
import MarkdownRenderer from '@/views/components/MarkdownRenderer.vue'

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
  <div class="flex flex-col p-6 h-screen overflow-hidden">
    <!--  Top bar  -->
    <div class="flex flex-row justify-between items-center">
      <div class="text-2xl font-bold">{{ examStore.details_resource.data.exam.title }}</div>
      <div class="flex flex-row gap-5 items-center">
        <p class="text-[1.8rem] font-bold">{{ examStore.time_left }}</p>
        <Button theme="green" variant="solid">
          Submit Exam
        </Button>
      </div>
    </div>
    <!--  Content  -->
    <div class="flex flex-row h-full gap-4 mt-5">
      <div id="exam-questions-container" class="flex flex-row h-full gap-2 w-full">
        <div :style="`width: ${questionPanelWidthPercentage}%`" class="border-2 h-full rounded-md p-4">
          <MarkdownRenderer
            :source="examStore.current_question.description" />
        </div>
        <div class="w-[5px] bg-gray-400 h-full rounded-md cursor-col-resize hover:bg-gray-500 focus:bg-gray-500"
             @mousedown="onSelectResizer"></div>
        <div :style="`width: ${answerPanelWidthPercentage}%`" class="h-full rounded-md border-2 p-4">
          <!--     Answers Panel   -->
          <!--    Text question      -->
          <div v-if="examStore.current_question.type === 'text'">
            <p class="text-black font-medium mb-3">Write down the answer here.</p>
            <FormControl
              :disabled="false"
              label=""
              placeholder="Placeholder"
              rows="30"
              size="lg"
              type="textarea"
              variant="outline"
            />
            <div v-if="examStore.current_question" class="flex w-full justify-end mt-2 gap-2">
              <Button theme="gray" variant="outline">
                Skip this question
              </Button>
              <Button theme="gray" variant="solid">
                Submit & Proceed to Next Question
              </Button>
            </div>
          </div>
          <!--    Multiple choice question      -->
          <div v-else-if="examStore.current_question.type === 'mcq'">
            <p class="text-black font-medium mb-3">Select the correct answer</p>
            <div class="flex flex-col gap-3">
              <div v-for="(option, index) in examStore.current_question.mcq_question_choices" :key="index"
                   :class="{
                    'border-black': examStore.get_current_question_answer === option,
                   }"
                   class="px-4 py-2 rounded-md hover:ring-1 cursor-pointer ring-gray-400 border-2 transition-all"
                   @click="examStore.submit_answer(option)"
              >
                {{ option }}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
    <!--  Question Switcher  -->
    <div class="flex flex-row items-center justify-center mt-4 gap-3">
      <Button icon-left="arrow-left" variant="outline">Previous</Button>
      <div v-for="(_, index) in examStore.question_series" :key="index"
           :class="{
          'border': examStore.current_question_index !== index,
          'border-2 border-black' : examStore.current_question_index === index
        }"
           class="h-full aspect-square rounded-sm flex justify-center items-center text-base cursor-pointer transition-all"
           @click="examStore.switch_question(index)"
      >
        {{ index + 1 }}
      </div>
      <Button icon-right="arrow-right" variant="outline">Next</Button>
    </div>
  </div>
</template>

<style scoped>

</style>