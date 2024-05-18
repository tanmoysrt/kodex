import { defineStore } from 'pinia'
import { createResource, toast } from 'frappe-ui'
import { computed, nextTick, ref, shallowRef } from 'vue'

export const useExam = defineStore('exam_management', () => {
  const exam_creds_base64 = shallowRef('')
  const exam_creds_invalid = ref(false)
  const auth_token = shallowRef('')
  const details_resource = createResource({
    method: 'POST',
    url: 'kodex.api.get_examination_details',
    onSuccess: on_success_fetch_exam_registration_details
  })
  const is_video_monitoring_enabled = ref(false)
  const is_full_screen_mode_enabled = ref(false)
  const local_clipboard = shallowRef('')
  const is_exam_started = ref(false)
  const locally_full_screen_mode_enabled = ref(false)
  const locally_webcam_feed_enabled = ref(false)

  const set_locally_full_screen_mode_enabled = (value) => {
    locally_full_screen_mode_enabled.value = value
  }
  const set_locally_webcam_feed_enabled = (value) => {
    locally_webcam_feed_enabled.value = value
  }

  const fetch_exam_registration_resource = (credsBase64) => {
    try {
      exam_creds_base64.value = credsBase64
      auth_token.value = JSON.parse(atob(credsBase64)).auth_token
      details_resource.fetch({
        exam_registration_name: JSON.parse(atob(credsBase64)).name,
        auth_token: auth_token.value
      })
      return true
    } catch (e) {
      return false
    }
  }

  function on_success_fetch_exam_registration_details(details) {
    if (!details.found) {
      exam_creds_invalid.value = true
      toast({
        title: 'Invalid',
        position: 'top-center',
        text: 'Invalid details',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    is_video_monitoring_enabled.value = details.proctoring.video_proctoring.enabled
    is_full_screen_mode_enabled.value = details.proctoring.full_screen_mode
    // enable other restrictions
    enable_proctoring_restrictions()
  }

  function enable_proctoring_restrictions() {
    if (!details_resource.data.proctoring) {
      return
    }
    if (details_resource.data.proctoring.right_click_disabled) {
      document.addEventListener('contextmenu', event => event.preventDefault())
    }
    if (details_resource.data.proctoring.devtools_disabled) {
      document.addEventListener('contextmenu', event => event.preventDefault())
      document.addEventListener('keydown', event => {
        if (event.key === 'F12') {
          event.preventDefault()
        }
        if (event.ctrlKey && event.shiftKey && (
          event.key === 'I' || event.key === 'J' || event.key === 'C'
        )) {
          event.preventDefault()
        }
        if (event.ctrlKey && event.key === 'U') {
          event.preventDefault()
        }
      })
    }
    if (details_resource.data.proctoring.copy_paste_disabled) {
      document.addEventListener('cut', async function(e) {
        const selection = document.getSelection()
        local_clipboard.value = selection.toString()
        selection.deleteFromDocument()
        e.preventDefault()
        await nextTick()
      })
      document.addEventListener('copy', async function(e) {
        const selection = document.getSelection()
        local_clipboard.value = selection.toString()
        selection.deleteFromDocument()
        e.preventDefault()
        await nextTick()
      })
      document.addEventListener('paste', async function(e) {
        e.preventDefault()
        const activeElement = document.activeElement
        let currentText = activeElement.value
        let selectionStart = activeElement.selectionStart
        await nextTick()
        e.target.value = currentText.substring(0, selectionStart) + local_clipboard.value + currentText.substring(activeElement.selectionEnd)
        const cursorPosition = selectionStart + local_clipboard.value.length
        activeElement.selectionStart = cursorPosition
        activeElement.selectionEnd = cursorPosition
      })
      // disable ctrl+z and ctrl+y
      document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && (e.key === 'Z' || e.key === 'Y' || e.key === 'z' || e.key === 'y')) {
          e.preventDefault()
        }
      })
    }
  }

  function start_exam() {
    if (!(navigator.userAgent.indexOf('Firefox') === -1 && navigator.userAgent.indexOf('Chrome') !== -1)) {
      toast({
        title: 'Only Chrome is supported',
        position: 'top-right',
        text: 'Please use Chrome or Chromium browser to start the exam',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }

    if (details_resource.data.proctoring.full_screen_mode && !is_full_screen_mode_enabled.value) {
      toast({
        title: 'Full Screen Mode is disabled',
        position: 'top-right',
        text: 'Please enable full screen mode to start the exam',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
    }
    if (is_video_monitoring_enabled.value && !locally_webcam_feed_enabled.value) {
      toast({
        title: 'Webcam feed is disabled',
        position: 'top-right',
        text: 'Please enable webcam  to start the exam',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
    }

  }

  return {
    fetch_exam_registration_resource,
    exam_creds_invalid,
    details_resource,
    is_video_monitoring_enabled,
    is_full_screen_mode_enabled,
    is_exam_started,
    set_locally_full_screen_mode_enabled,
    set_locally_webcam_feed_enabled,
    start_exam
  }
})