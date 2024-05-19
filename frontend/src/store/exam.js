import { defineStore } from 'pinia'
import { createResource, toast } from 'frappe-ui'
import { computed, nextTick, ref, shallowRef } from 'vue'

export const useExam = defineStore('exam_management', () => {
  const exam_creds_base64 = shallowRef('')
  const exam_creds_invalid = ref(false)
  const auth_token = shallowRef('')
  const is_video_monitoring_enabled = ref(false)
  const is_full_screen_mode_enabled = ref(false)
  const local_clipboard = shallowRef('')
  const is_exam_started = ref(false)
  const locally_full_screen_mode_enabled = ref(false)
  const locally_webcam_feed_enabled = ref(false)
  const set_locally_full_screen_mode_enabled = (value) => locally_full_screen_mode_enabled.value = value
  const set_locally_webcam_feed_enabled = (value) => locally_webcam_feed_enabled.value = value
  const details_resource = createResource({
    method: 'POST',
    url: 'kodex.api.get_examination_details',
    onSuccess: on_success_fetch_exam_registration_details
  })
  const submit_proctoring_images_resource = createResource({
    method: 'POST',
    url: 'kodex.api.submit_proctoring_images'
  })
  const question_details_resource = createResource({
    method: 'POST',
    url: 'kodex.api.download_questions',
    onSuccess: on_success_fetch_question_details
  })
  const question_series = ref([])
  const questions = ref({})
  const answers = ref({})
  const current_question_index = ref(0)
  const end_time = ref(null)
  const start_time = ref(null)
  const time_left = ref('--:--')

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

  function start_video_proctoring() {
    if (!details_resource.data.proctoring.video_proctoring.enabled) return
    const images_per_minute = details_resource.data.proctoring.video_proctoring.no_of_pictures_per_minute
    setInterval(function() {
      try {
        const video = document.getElementById('webcam')
        const canvas = document.createElement('canvas')
        canvas.width = video.clientWidth
        canvas.height = video.clientHeight
        canvas.getContext('2d').drawImage(video, 0, 0, video.clientWidth, video.clientHeight)
        submit_proctoring_images_resource.fetch({
          exam_registration_name: details_resource.data.registration_name,
          auth_token: auth_token.value,
          image_b64: canvas.toDataURL('image/png').split(',')[1]
        })
      } catch (e) {
        console.log('failed to submit image')
      }
    }, (60 / images_per_minute) * 1000)
  }

  function on_success_fetch_question_details(data) {
    // actual exam started
    is_exam_started.value = true
    question_series.value = data.question_series
    questions.value = data.questions
    answers.value = data.answers
    // start time_left timer
    start_time.value = details_resource.data.session.candidate_started_on != null ? new Date(details_resource.data.session.candidate_started_on) : start_time.value
    end_time.value = new Date(start_time.value.getTime() + details_resource.data.session.login_window_minutes * 60000)
    setInterval(function() {
      time_left.value = formattedTimeLeft()
    }, 1000)
  }

  const formattedTimeLeft = () => {
    const currentTime = new Date()
    const timeDiff = end_time.value - currentTime
    const totalSeconds = Math.max(0, Math.floor(timeDiff / 1000))
    const minutes = Math.floor(totalSeconds / 60)
    const seconds = totalSeconds % 60
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
  }

  function start_exam() {
    document.getElementsByTagName('body')[0].style.backgroundImage = `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='200px' width='200px'><text transform='translate(20, 100) rotate(-45)' fill='rgb(210,210,210)' font-size='20'>${details_resource.data.candidate.email}</text></svg>");`
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

    if (details_resource.data.proctoring.full_screen_mode && !locally_full_screen_mode_enabled.value) {
      toast({
        title: 'Full Screen Mode is disabled',
        position: 'top-right',
        text: 'Please enable full screen mode to start the exam',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    if (is_video_monitoring_enabled.value && !locally_webcam_feed_enabled.value) {
      toast({
        title: 'Webcam feed is disabled',
        position: 'top-right',
        text: 'Please enable webcam  to start the exam',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    if (details_resource.data.proctoring.devtools_disabled) {
      setInterval(() => {
        debugger;
      }, 1000)
    }
    if (details_resource.data.proctoring.watermark_candidate_id) {
      const svgString = `<svg xmlns='http://www.w3.org/2000/svg' version='1.1' height='200px' width='400px'><text transform='translate(40, 180) rotate(-25)' fill='rgb(220,220,220)' font-size='20'>${details_resource.data.candidate.email}</text></svg>`
      document.body.style.backgroundImage = `url("data:image/svg+xml,${encodeURIComponent(svgString)}")`
    }
    start_video_proctoring()
    start_time.value = new Date()
    question_details_resource.fetch({
      exam_registration_name: details_resource.data.registration_name,
      auth_token: auth_token.value
    })
  }

  const switch_question = (index) => {
    current_question_index.value = index
  }

  const submit_answer = (answer) => {
    answers.value[current_question.value.name] = answer
  }

  const get_current_question_answer = computed(() => {
    if (current_question.value.name in answers.value) {
      return answers.value[current_question.value.name]
    }
    return ''
  })

  const current_question = computed(() => questions.value[question_series.value[current_question_index.value]])

  return {
    fetch_exam_registration_resource,
    exam_creds_invalid,
    details_resource,
    is_video_monitoring_enabled,
    is_full_screen_mode_enabled,
    is_exam_started,
    set_locally_full_screen_mode_enabled,
    set_locally_webcam_feed_enabled,
    question_details_resource,
    start_exam,
    questions,
    answers,
    question_series,
    current_question_index,
    time_left,
    start_time,
    end_time,
    switch_question,
    current_question,
    submit_answer,
    get_current_question_answer
  }
})