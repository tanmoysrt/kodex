<script setup>
import WebcamFeed from '@/views/partials/WebcamFeed.vue'
import FullScreenMode from '@/views/partials/FullScreenMode.vue'
import ExamWelcome from '@/views/pages/ExamWelcome.vue'
import { useExam } from '@/store/exam'
import ExamQuestions from '@/views/pages/ExamQuestions.vue'

const examStore = useExam()

</script>
<template>
  <teleport to="body">
    <WebcamFeed />
  </teleport>
  <teleport to="body">
    <FullScreenMode />
  </teleport>
  <ExamWelcome v-if="!examStore.is_exam_started" />
  <ExamQuestions v-else />
</template>
