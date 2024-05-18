<script setup>

import { onMounted, reactive, ref } from 'vue'
import { Button, Dialog, Select } from 'frappe-ui'
import { useExam } from '@/store/exam'

const examStore = useExam()
const positions = reactive({
  'pos1': 0,
  'pos2': 0,
  'pos3': 0,
  'pos4': 0,
  'height': 200,
  'width': 300
})
const isVideoStreamStarted = ref(false)
const videoDevices = ref([])
const cameraSelectionDialog = ref(false)
const selectedDeviceId = ref('')

const defaultTop = () => {
  return window.innerHeight - positions.height - 10
}

const dragDiv = (e) => {
  e.preventDefault()
  positions.pos3 = e.clientX
  positions.pos4 = e.clientY
  document.onmouseup = () => {
    document.onmouseup = null
    document.onmousemove = null
  }
  document.onmousemove = (e2) => {
    e2.preventDefault()
    positions.pos1 = positions.pos3 - e2.clientX
    positions.pos2 = positions.pos4 - e2.clientY
    positions.pos3 = e2.clientX
    positions.pos4 = e2.clientY
    const element = document.getElementById('video-feed-container')
    element.style.top = Math.max(Math.min((element.offsetTop - positions.pos2), (window.innerHeight - positions.height - 10)), 10) + 'px'
    element.style.left = Math.max(Math.min((element.offsetLeft - positions.pos1), (window.innerWidth - positions.width - 10)), 10) + 'px'
  }
}

const startCamera = async () => {
  // Check if the Permissions API is supported
  if (navigator.permissions && navigator.permissions.query) {
    try {
      const permissionStatus = await navigator.permissions.query({ name: 'camera' })

      if (permissionStatus.state === 'granted') {
        // Access already granted, start the webcam
        await getVideoDevices()
      } else if (permissionStatus.state === 'prompt') {
        // Prompt the user for access
        await getVideoDevices()
      } else if (permissionStatus.state === 'denied') {
        alert('Webcam access denied.')
      }
    } catch (error) {
      alert(`Permission query error: ${error.message}`)
    }
  } else {
    alert('Permissions API is not supported in this browser.')
  }
}

const getVideoDevices = async () => {
  try {
    const initStream = await navigator.mediaDevices.getUserMedia({ video: true })
    try {
      initStream.getTracks().forEach(track => track.stop())
    } catch (e) {
      console.log('failed to stop init stream')
    }
    const devices = await navigator.mediaDevices.enumerateDevices()
    videoDevices.value = devices.filter(device => device.kind === 'videoinput')
    cameraSelectionDialog.value = true
  } catch (error) {
    if (error.name === 'NotAllowedError') {
      alert('Webcam access denied.')
    } else if (error.name === 'NotFoundError') {
      alert('No webcam found.')
    } else {
      alert(`Error: ${error.message}`)
    }
  }
}

const startVideoStream = async () => {
  cameraSelectionDialog.value = false
  try {
    if (selectedDeviceId.value) {
      isVideoStreamStarted.value = true
      const videoElement = document.getElementById('webcam')
      videoElement.srcObject = await navigator.mediaDevices.getUserMedia({ video: { deviceId: { exact: selectedDeviceId.value } } })
      examStore.set_locally_webcam_feed_enabled(true)
    }
  } catch (error) {
    if (error.name === 'NotAllowedError') {
      alert('Webcam access denied.')
    } else if (error.name === 'NotFoundError') {
      alert('No webcam found.')
    } else {
      alert(`Error: ${error.message}`)
    }
  }
}

onMounted(() => {
  window.addEventListener('resize', () => {
    if (examStore.is_video_monitoring_enabled) {
      document.getElementById('video-feed-container').style.top = defaultTop() + 'px'
      document.getElementById('video-feed-container').style.left = '10px'
    }
  })
})

</script>

<template>
  <div v-show="examStore.is_video_monitoring_enabled"
       id="video-feed-container"
       :style="`width: ${positions.width}px; height: ${positions.height}px; top: ${defaultTop()}px; left: 10px`"
       class="block border-4 shadow-sm absolute z-10 bg-white cursor-pointer select-none rounded-md p-2 overflow-hidden "
       @mousedown="dragDiv">
    <div v-if="!isVideoStreamStarted" class="w-full h-full flex justify-center items-center">
      <Button icon-left="video" variant="solid" @click="startCamera">Start Camera</Button>
    </div>
    <video id="webcam" :style="`width: ${positions.width-20}px; height: ${positions.height-20}px; object-fit: cover`"
           autoplay
           class="rounded-sm"></video>
  </div>
  <Dialog v-model="cameraSelectionDialog">
    <template #body-title>
      <p class="font-medium">Choose webcam device</p>
    </template>
    <template #body-content>
      <Select
        v-model="selectedDeviceId"
        :options="videoDevices.map((device, index) => ({ label: device.label, value: device.deviceId }))"
      />
    </template>
    <template #actions>
      <Button :disabled="!selectedDeviceId" variant="solid" @click="startVideoStream">
        Confirm
      </Button>
      <Button
        class="ml-2"
        @click="cameraSelectionDialog = false"
      >
        Close
      </Button>
    </template>
  </Dialog>
</template>

<style scoped>

</style>