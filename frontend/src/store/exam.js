import { defineStore } from 'pinia'
import { createResource, toast } from 'frappe-ui'
import { computed, nextTick, ref, shallowRef } from 'vue'
import { useRouter } from 'vue-router'

export const useExam = defineStore('exam_management', () => {
  const router = useRouter()
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
  const answers_language_id = ref({})
  const tmp_answers_store = ref({})
  const current_question_index = ref(0)
  const end_time = ref(null)
  const start_time = ref(null)
  const time_left = ref('--:--')
  const available_languages = ref([])
  const current_language = ref('')
  const test_cases_result_status = ref({})
  // "id": 1 (success), 0 (failed), 2 (running), -1 or not available none
  const test_cases_result = ref({})
  const is_answer_submitting = ref(false)
  const submit_exam_resource = createResource({
    method: 'POST',
    url: 'kodex.api.submit_and_end_exam',
    onSuccess: () => {
      router.push({
        name: "Exam Completed",
        replace: true
      })
    }
  })
  const submit_exam_for_malpractice_resource = createResource({
    method: 'POST',
    url: 'kodex.api.end_exam_due_to_malpractice',
    onSuccess: () => {
      router.push({
        name: "Exam Completed Due To Malpractice",
        replace: true
      })
    }
  })

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
      document.addEventListener('cut', async function (e) {
        const selection = document.getSelection()
        local_clipboard.value = selection.toString()
        selection.deleteFromDocument()
        e.preventDefault()
        await nextTick()
      })
      document.addEventListener('copy', async function (e) {
        const selection = document.getSelection()
        local_clipboard.value = selection.toString()
        selection.deleteFromDocument()
        e.preventDefault()
        await nextTick()
      })
      document.addEventListener('paste', async function (e) {
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
      document.addEventListener('keydown', function (e) {
        if (e.ctrlKey && (e.key === 'Z' || e.key === 'Y' || e.key === 'z' || e.key === 'y')) {
          e.preventDefault()
        }
      })
    }
  }

  function start_video_proctoring() {
    if (!details_resource.data.proctoring.video_proctoring.enabled) return
    const images_per_minute = details_resource.data.proctoring.video_proctoring.no_of_pictures_per_minute
    setInterval(function () {
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
    if(!data.question_series) return
    if(data.question_series.length === 0) {
      toast({
        title: 'Contact admin',
        position: 'top-center',
        text: 'No questions available',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    question_series.value = data.question_series
    questions.value = data.questions
    answers.value = data.answers
    answers_language_id.value = data.answers_language_id
    switch_question(0)
    // start time_left timer
    start_time.value = details_resource.data.session.candidate_started_on != null ? new Date(details_resource.data.session.candidate_started_on) : start_time.value
    end_time.value = new Date(start_time.value.getTime() + details_resource.data.session.login_window_minutes * 60000)
    setInterval(function () {
      time_left.value = formattedTimeLeft()
    }, 1000)
    // start exam
    is_exam_started.value = true
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

  const previous_question_button_enbaled = computed(() => current_question_index.value > 0)
  const next_question_button_enabled = computed(() => current_question_index.value + 1 < question_series.value.length)

  const previous_question = () => {
    if (current_question_index.value <= 0) return
    switch_question(current_question_index.value - 1)
  }

  const next_question = () => {
    if (current_question_index.value + 1 >= question_series.value.length) return
    switch_question(current_question_index.value + 1)
  }

  const switch_question = (index) => {
    let question = questions.value[question_series.value[index]];
    // clear answers if not submitted, else take the answer from submitted answers mapping
    if (question.name in answers.value) {
      tmp_answers_store.value[question.name] = answers.value[question.name]
    } else {
      tmp_answers_store.value[question.name] = ""
    }
    // clear results of coding
    test_cases_result.value = {}
    test_cases_result_status.value = {}
    // set coding question params
    if (question.type === 'coding') {
      available_languages.value = questions.value[question_series.value[index]].coding_question.available_languages
      if (question.name in answers_language_id.value){
        if(answers_language_id.value[question.name] === ''){
          current_language.value = available_languages.value[0].id
        } else {
          current_language.value = answers_language_id.value[question.name]
        }
      } else {
        current_language.value = available_languages.value[0].id
      }
    } else {
      current_language.value = ''
    }
    current_question_index.value = index
  }

  const temp_store_answer = (answer) => {
    tmp_answers_store.value[current_question.value.name] = answer
  }

  const get_current_question_answer = computed(() => {
    if (current_question.value.name in tmp_answers_store.value) {
      return tmp_answers_store.value[current_question.value.name]
    }
    return ''
  })

  const current_question = computed(() => questions.value[question_series.value[current_question_index.value]])
  const is_last_question = computed(() => current_question_index.value + 1 >= question_series.value.length)

  const switch_language = (event) => {
    current_language.value = event.target.value
  }

  const test_code = (index) => {
    if (get_current_question_answer.value === '') {
      toast({
        title: 'Code run failed',
        position: 'top-right',
        text: 'You can\'t submit blank code',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    const test_case = current_question.value.coding_question.test_cases[index]
    test_cases_result_status.value[test_case.name] = 2
    const request = createResource({
      method: 'POST',
      url: 'kodex.api.run_code',
      onSuccess: async function (response) {
        let code_runner_id = response.id
        let code_runner_access_token = response.access_token
        let result_api = createResource({
          method: 'POST',
          url: 'kodex.api.get_code_result',
          onSuccess: function (response) {
            if (response.status === 'failed') {
              test_cases_result_status.value[test_case.name] = 0
            } else if (response.status === 'completed') {
              test_cases_result_status.value[test_case.name] = 1
            }
            test_cases_result.value[test_case.name] = response
          }
        })
        while (test_cases_result_status.value[test_case.name] === 2) {
          await new Promise(resolve => setTimeout(resolve, 3000))
          result_api.fetch({
            exam_registration_name: details_resource.data.registration_name,
            auth_token: auth_token.value,
            code_runner_id: code_runner_id,
            code_runner_access_token: code_runner_access_token
          })
          await result_api.promise
        }
      }
    })
    request.fetch({
      exam_registration_name: details_resource.data.registration_name,
      auth_token: auth_token.value,
      source_code_base64: btoa(get_current_question_answer.value),
      language_id: current_language.value,
      input_base64: btoa(test_case.input)
    })
  }

  function run_all_test_cases() {
    if (get_current_question_answer.value === '') {
      toast({
        title: 'Code run failed',
        position: 'top-right',
        text: 'You can\'t submit blank code',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    for (let i = 0; i < current_question.value.coding_question.test_cases.length; i++) {
      test_code(i)
    }
  }

  async function submit_answer() {
    if (!get_current_question_answer.value) {
      toast({
        title: 'Empty Answer',
        position: 'top-center',
        text: 'Write / select answer',
        icon: 'x-circle',
        iconClasses: 'text-red-500'
      })
      return
    }
    const question = current_question.value.name;
    const answer = get_current_question_answer.value;
    is_answer_submitting.value = true;
    const request = createResource({
      method: 'POST',
      url: 'kodex.api.submit_answer',
      onSuccess: async function () {
        answers.value[question] = answer
        answers_language_id.value[question] = current_language.value
        next_question()
        is_answer_submitting.value = false;
        toast({
          title: 'Answer Submitted',
          position: 'top-center',
          icon: 'check-circle',
          iconClasses: 'text-green-500'
        })
      },
      onError: async function () {
        toast({
          title: 'Failed to submit',
          position: 'top-center',
          text: 'Retry to submit',
          icon: 'x-circle',
          iconClasses: 'text-red-500'
        })
        is_answer_submitting.value = false;
      },
    })
    request.fetch({
      exam_registration_name: details_resource.data.registration_name,
      auth_token: auth_token.value,
      question_name: current_question.value.name,
      answer_base64: btoa(get_current_question_answer.value),
      language_id: current_language.value
    })
    return request.promise
  }

  const submit_exam = () => {
    submit_exam_resource.fetch({
      exam_registration_name: details_resource.data.registration_name,
      auth_token: auth_token.value,
    })
  }

  const submit_exam_for_malpractice = (reason) => {
    submit_exam_for_malpractice_resource.fetch({
      exam_registration_name: details_resource.data.registration_name,
      auth_token: auth_token.value,
      reason: reason
    })
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
    question_details_resource,
    start_exam,
    questions,
    tmp_answers_store,
    question_series,
    current_question_index,
    time_left,
    start_time,
    end_time,
    switch_question,
    current_question,
    temp_store_answer,
    get_current_question_answer,
    available_languages,
    current_language,
    switch_language,
    test_code,
    test_cases_result_status,
    test_cases_result,
    run_all_test_cases,
    previous_question_button_enbaled,
    next_question_button_enabled,
    previous_question,
    next_question,
    submit_answer,
    is_answer_submitting,
    answers,
    submit_exam_resource,
    submit_exam,
    submit_exam_for_malpractice_resource,
    submit_exam_for_malpractice,
    is_last_question
  }
})