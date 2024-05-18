import base64

import frappe
from kodex.kodex.doctype.code_runner.code_runner import CodeRunner
from kodex.kodex.doctype.examination_question_attempt.examination_question_attempt import (
    ExaminationQuestionAttempt,
)


@frappe.whitelist(allow_guest=True, methods=["POST"])
def get_examination_details(exam_registration_name, auth_token):
    try:
        record = frappe.get_cached_doc(
            "Examination Candidate Registration", exam_registration_name
        )
        record.check_auth(auth_token)
        is_valid_to_start, message = record.validate_for_starting_exam()
        exam_details = frappe.get_cached_doc("Examination", record.examination)
        candidate_details = frappe.get_cached_doc("User", record.candidate)
        return {
            "found": True,
            "registration_name": record.name,
            "exam": {
                "title": exam_details.exam_name,
                "description": exam_details.description,
                "total_questions": exam_details.total_questions,
                "total_marks": exam_details.total_marks,
            },
            "candidate": {
                "first_name": (
                    candidate_details.first_name if candidate_details.first_name else ""
                ),
                "last_name": (
                    candidate_details.last_name if candidate_details.last_name else ""
                ),
                "email": candidate_details.email,
            },
            "proctoring": {
                "full_screen_mode": bool(exam_details.full_screen_mode),
                "watermark_candidate_id": bool(exam_details.watermark_candidate_id),
                "auto_submit_exam_on_focus_lose": bool(
                    exam_details.auto_submit_exam_on_focus_lose
                ),
                "copy_paste_disabled": bool(exam_details.copy_paste_disabled),
                "right_click_disabled": bool(exam_details.right_click_disabled),
                "devtools_disabled": bool(exam_details.devtools_disabled),
                "video_proctoring": {
                    "enabled": bool(exam_details.video_proctoring),
                    "no_of_pictures_per_minute": exam_details.no_of_pictures_per_minute,
                },
            },
            "session": {
                "notice": message,
                "is_valid": is_valid_to_start,
                "is_started": record.is_exam_started(),
                "start_time": record.start_time,
                "start_time_formatted": frappe.utils.get_datetime(
                    record.start_time
                ).strftime("%d-%m-%Y %I:%M %p"),
                "end_time": record.end_time,
                "end_time_formatted": frappe.utils.get_datetime(
                    record.end_time
                ).strftime("%d-%m-%Y %I:%M %p"),
                "login_window_minutes": record.login_window_minutes,
                "candidate_started_on": record.exam_started_on,
                "candidate_started_on_formatted": (
                    frappe.utils.get_datetime(record.exam_started_on).strftime(
                        "%d-%m-%Y %I:%M %p"
                    )
                    if record.exam_started_on
                    else ""
                ),
            },
        }
    except frappe.DoesNotExistError:
        return {
            "found": False,
        }


@frappe.whitelist(allow_guest=True, methods=["POST"])
def download_questions(exam_registration_name, auth_token):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    record.start_exam()
    exam_record = frappe.get_cached_doc("Examination", record.examination)
    return exam_record.get_questions_for_candidate()


@frappe.whitelist(allow_guest=True, methods=["POST"])
def run_code(
    exam_registration_name, auth_token, source_code_base64, language_id, input_base64
):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    res = CodeRunner.run_code(
        base64.b64decode(source_code_base64).decode("utf-8"),
        language_id,
        base64.b64decode(input_base64).decode("utf-8"),
    )
    return {"id": res[0], "access_token": res[1]}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def get_code_result(
    exam_registration_name, auth_token, code_runner_id, code_runner_access_token
):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    result = frappe.get_doc(
        "Code Runner",
        {"name": code_runner_id, "access_token": code_runner_access_token},
    )
    return {
        "status": result.status,
        "status_description": result.debug_judge0_status_description,
        "time_second": result.time_second,
        "memory_kb": result.memory_kb,
        "input": result.input,
        "output": result.output,
        "error": result.error,
        "compile_output": result.compile_output,
    }


@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_answer(exam_registration_name, auth_token, question_name, answer_base64):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    try:
        ExaminationQuestionAttempt.record(
            exam_registration_name,
            question_name,
            base64.b64decode(answer_base64).decode("utf-8"),
        )
        return "ok"
    except Exception as e:
        frappe.log_error("failed to record answer", message=e)
        frappe.throw("failed to record answer")


@frappe.whitelist(allow_guest=True, methods=["POST"])
def get_submitted_answers(exam_registration_name, auth_token):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    return frappe.get_list(
        "Examination Question Attempt",
        filters={"examination_candidate_registration": exam_registration_name},
        fields=["question", "submitted_answer"],
        ignore_permissions=True,
    )


@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_and_end_exam(exam_registration_name, auth_token):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    record.end_exam()
    return "ok"


@frappe.whitelist(allow_guest=True, methods=["POST"])
def end_exam_due_to_malpractice(exam_registration_name, auth_token, reason):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    record.end_exam_due_to_malpractice(reason)
    return "ok"


@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_proctoring_images(exam_registration_name, auth_token, image_b64):
    record = frappe.get_cached_doc(
        "Examination Candidate Registration", exam_registration_name
    )
    record.check_auth(auth_token)
    is_valid_to_start, message = record.validate_for_starting_exam()
    if not is_valid_to_start:
        return frappe.throw(message)
    image = base64.b64decode(image_b64, validate=True)
    _file = frappe.get_doc(
        {
            "doctype": "File",
            "file_name": frappe.utils.random_string(20) + ".png",
            "attached_to_doctype": "Examination Candidate Registration",
            "attached_to_name": exam_registration_name,
            "content": image,
            "decode": False,
            "is_private": True,
        }
    )
    _file.save(ignore_permissions=True)
    return "ok"
