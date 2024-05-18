<script setup>
import { useRoute } from 'vue-router'
import { onMounted } from 'vue'
import { Button } from 'frappe-ui'
import MarkdownRenderer from '@/views/components/MarkdownRenderer.vue'
import WebcamFeed from '@/views/partials/WebcamFeed.vue'
import { useExam } from '@/store/exam'
import FullScreenMode from '@/views/partials/FullScreenMode.vue'


const route = useRoute()
const examStore = useExam()

onMounted(() => {
  if (!examStore.fetch_exam_registration_resource(route.params.info)) {
    alert('Invalid')
  }
})

</script>
<template>
  <teleport to="body">
    <WebcamFeed />
  </teleport>
  <teleport to="body">
    <FullScreenMode />
  </teleport>
  <div v-if="examStore.details_resource.loading">Loading...</div>
  <div v-else-if="examStore.exam_creds_invalid"> Invalid exam credentials</div>
  <div v-else-if="examStore.details_resource.data" class="flex flex-col ">
    <!--  exam title  -->
    <div class="text-2xl font-bold w-full text-center mt-3 mb-10">{{ examStore.details_resource.data.exam.title }}</div>
    <!--  exam details  -->
    <div class="w-full flex flex-row justify-evenly gap-5">
      <!--   Exam description   -->
      <div class="flex w-7/12 p-4 border  h-[75vh] overflow-y-auto rounded-md custom-scroll">
        <MarkdownRenderer :source="examStore.details_resource.data.exam.description" />
      </div>
      <div class="flex flex-col w-4/12 gap-6">
        <!--    Candidate Information    -->
        <div>
          <p class="text-xl font-bold">Candidate Information</p>
          <div class="flex flex-col gap-1 mt-2">
            <p class="font-medium">Name - <span
              class="font-normal">{{ examStore.details_resource.data.candidate.first_name
              }} {{ examStore.details_resource.data.candidate.last_name }}</span></p>
            <p class="font-medium">Email - <span class="font-normal">{{ examStore.details_resource.data.candidate.email
              }}</span>
            </p>
          </div>
        </div>
        <!--   Exam details     -->
        <div>
          <p class="text-xl font-bold">Exam Details</p>
          <div class="flex flex-col gap-1 mt-2">
            <p class="font-medium">Duration - <span
              class="font-normal">{{ examStore.details_resource.data.session.login_window_minutes }} minutes</span></p>
            <p class="font-medium">Start Time - <span
              class="font-normal">{{ examStore.details_resource.data.session.start_time_formatted }}</span></p>
            <p class="font-medium">End Time - <span
              class="font-normal">{{ examStore.details_resource.data.session.end_time_formatted }}</span></p>
            <p class="font-medium">Total Marks - <span
              class="font-normal">{{ examStore.details_resource.data.exam.total_marks
              }}</span></p>
            <p class="font-medium">Total Questions - <span
              class="font-normal">{{ examStore.details_resource.data.exam.total_questions }}</span></p>
          </div>
        </div>
      </div>
    </div>
    <!-- notice and action button   -->
    <div class="flex flex-row justify-center w-full gap-6 absolute bottom-5 left-0 right-0">
      <p
        :class="{
        'text-red-500': !examStore.details_resource.data.session.is_valid,
        'text-green-500': examStore.details_resource.data.session.is_valid
      }"
        class="font-medium">{{ examStore.details_resource.data.session.notice }}</p>
      <Button :disabled="!examStore.details_resource.data.session.is_valid" theme="gray"
              variant="solid"
              @click="examStore.start_exam">
        {{ examStore.details_resource.data.session.is_started ? 'Resume Exam' : 'Start Exam' }}
      </Button>
    </div>
  </div>
</template>
