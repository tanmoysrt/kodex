<script setup>

import { useExam } from '@/store/exam'
import { Button } from 'frappe-ui'
import { nextTick, onMounted, ref, watch } from 'vue'

const exam_store = useExam()
const is_full_screen_enabled = ref(false)
const full_screen_mode_entered = ref(false)
const seconds_left_from_auto_submit = ref(20)

function enable_full_screen_mode() {
  if (document.fullscreenEnabled) {
    document.documentElement.requestFullscreen()
  } else if (document.webkitFullscreenEnabled) {
    document.documentElement.webkitRequestFullscreen()
  } else if (document.mozFullScreenEnabled) {
    document.documentElement.mozRequestFullScreen()
  } else if (document.msFullscreenEnabled) {
    document.documentElement.msRequestFullscreen()
  }
}

function isFullScreen() {
  return !!document.fullscreenElement
}

async function monitor() {
  if (!exam_store.is_full_screen_mode_enabled) return
  if (isFullScreen()) {
    is_full_screen_enabled.value = true
    full_screen_mode_entered.value = true
    seconds_left_from_auto_submit.value = 20
    exam_store.set_locally_full_screen_mode_enabled(true)
  } else {
    exam_store.set_locally_full_screen_mode_enabled(false)
    if (!exam_store.is_exam_started) return
    is_full_screen_enabled.value = false
    if (full_screen_mode_entered.value) {
      seconds_left_from_auto_submit.value--
    }
  }
}

watch(seconds_left_from_auto_submit, (val) => {
  if (val <= 0) {
    alert('Exam has been automatically submitted and flagged as failed')
  }
})

onMounted(() => {
  setInterval(monitor, 1000)
})
</script>

<template>
  <div v-if="exam_store.is_full_screen_mode_enabled && !is_full_screen_enabled"
       class="z-20 bg-white opacity-90 absolute top-0 left-0 w-full h-full flex flex-col gap-8 justify-center items-center">
    <Button icon-left="monitor" variant="solid" @click="enable_full_screen_mode">
      Enable Full Screen Mode
    </Button>
    <div v-if="full_screen_mode_entered" class="text-center">
      Enable Full Screen Mode within {{ seconds_left_from_auto_submit }} seconds<br>
      Else, exam will be automatically submitted and flagged as failed
    </div>
  </div>
</template>

<style scoped>

</style>