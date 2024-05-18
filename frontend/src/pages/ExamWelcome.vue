<script setup>
import { useRoute } from 'vue-router'
import { onMounted, ref } from 'vue'
import { createResource, Button, toast } from 'frappe-ui'
import MarkdownRenderer from '@/components/MarkdownRenderer.vue'


const route = useRoute()
const auth_token = ref('')
let exam_registration = createResource({
  method: 'POST',
  url: 'kodex.api.get_examination_details'
})

onMounted(() => {
  if(!route.params.info) {
    return
  }
  try {
    auth_token.value = JSON.parse(atob(route.params.info)).auth_token
    exam_registration.fetch({
      exam_registration_name: JSON.parse(atob(route.params.info)).name,
      auth_token: auth_token.value
    })
  } catch (e) {
    alert('Invalid exam registration name')
  }
  exam_registration.fetch()
  // document.addEventListener('contextmenu', event => event.preventDefault());
  // document.addEventListener('keydown', event => {
  //   if (event.key === 'F12') {
  //     event.preventDefault()
  //   }
  //   if (event.ctrlKey && event.shiftKey && (
  //     event.key === 'I' || event.key === 'J' || event.key === 'C'
  //   )) {
  //     event.preventDefault()
  //   }
  //   if (event.ctrlKey && event.key === 'U') {
  //     event.preventDefault()
  //   }
  // })
  // setTimeout(() => {
  //   toast({
  //     title: 'Success',
  //     position: 'top-right',
  //     text: 'File Uploaded Successfully!',
  //     icon: 'check',
  //     iconClasses: 'text-green-500',
  //   })
  // }, 1000)
})

</script>
<template>
  <div v-if="exam_registration.loading">Loading...</div>
  <div v-else-if="exam_registration.error"> {{ exam_registration.error }}</div>
  <div v-else-if="exam_registration.data" class="flex flex-col ">
    <!--  exam title  -->
    <div class="text-2xl font-bold w-full text-center mt-3 mb-10">{{ exam_registration.data.exam.title }}</div>
    <!--  exam details  -->
    <div class="w-full flex flex-row justify-evenly gap-5">
    <!--   Exam description   -->
      <div class="flex w-7/12 p-4 border  h-[75vh] overflow-y-auto rounded-md custom-scroll">
        <MarkdownRenderer :source="exam_registration.data.exam.description" />
      </div>
      <div class="flex flex-col w-4/12 gap-6">
        <!--    Candidate Information    -->
        <div>
          <p class="text-xl font-bold">Candidate Information</p>
          <div class="flex flex-col gap-1 mt-2">
            <p class="font-medium">Name - <span class="font-normal">{{ exam_registration.data.candidate.first_name }} {{ exam_registration.data.candidate.last_name }}</span></p>
            <p class="font-medium">Email - <span class="font-normal">{{ exam_registration.data.candidate.email }}</span></p>
          </div>
        </div>
        <!--   Exam details     -->
        <div>
          <p class="text-xl font-bold">Exam Details</p>
          <div class="flex flex-col gap-1 mt-2">
            <p class="font-medium">Duration - <span class="font-normal">{{ exam_registration.data.session.login_window_minutes }} minutes</span></p>
            <p class="font-medium">Start Time - <span class="font-normal">{{ exam_registration.data.session.start_time_formatted }}</span></p>
            <p class="font-medium">End Time - <span class="font-normal">{{ exam_registration.data.session.end_time_formatted }}</span></p>
            <p class="font-medium">Total Marks - <span class="font-normal">{{ exam_registration.data.exam.total_marks }}</span></p>
            <p class="font-medium">Total Questions - <span class="font-normal">{{ exam_registration.data.exam.total_questions }}</span></p>
          </div>
        </div>
      </div>
    </div>
    <!-- notice and action button   -->
    <div class="flex flex-row justify-center w-full gap-6 absolute bottom-5 left-0 right-0">
      <p
        class="font-medium"
        :class="{
        'text-red-500': !exam_registration.data.session.is_valid,
        'text-green-500': exam_registration.data.session.is_valid
      }">{{ exam_registration.data.session.notice }}</p>
      <Button theme="gray" variant="solid"
              :disabled="!exam_registration.data.session.is_valid">{{ exam_registration.data.session.is_started ? 'Resume Exam' : 'Start Exam' }}</Button>
    </div>
  </div>
</template>
