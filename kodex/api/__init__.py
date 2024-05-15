import frappe



@frappe.whitelist(allow_guest=True)
def get_examination_details(exam_registration_name, auth_token):
	record = frappe.get_doc("Examination Candidate Registration", exam_registration_name)
	record.check_auth(auth_token)
	is_valid_to_start, message = record.validate_for_starting_exam()
	exam_details = frappe.get_cached_doc("Examination", record.examination)
	candidate_details = frappe.get_cached_doc("User", record.candidate)
	return {
		"registration_name": record.name,
		"exam" : {
			"title": exam_details.exam_name,
			"description": exam_details.description,
			"total_questions": exam_details.total_questions,
			"total_marks": exam_details.total_marks,
		},
		"candidate": {
			"first_name": candidate_details.first_name if candidate_details.first_name else "",
			"last_name":candidate_details.last_name if candidate_details.last_name else "",
			"email": candidate_details.email,
		},
		"proctoring": {
			"full_screen_mode": exam_details.full_screen_mode,
			"watermark_candidate_id": exam_details.watermark_candidate_id,
			"auto_submit_exam_on_focus_lose": exam_details.auto_submit_exam_on_focus_lose,
			"copy_paste_disabled": exam_details.copy_paste_disabled,
			"right_click_disabled": exam_details.right_click_disabled,
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
			"start_time_formatted": frappe.utils.get_datetime(record.start_time).strftime("%d-%m-%Y %I:%M %p"),
			"end_time": record.end_time,
			"end_time_formatted": frappe.utils.get_datetime(record.end_time).strftime("%d-%m-%Y %I:%M %p"),
			"login_window_minutes": record.login_window_minutes,
		}
	}

@frappe.whitelist(allow_guest=True)
def download_questions(exam_registration_name, auth_token):
	record = frappe.get_doc("Examination Candidate Registration", exam_registration_name)
	record.check_auth(auth_token)
	is_valid_to_start, message = record.validate_for_starting_exam()
	if not is_valid_to_start:
		return frappe.throw(message)
	exam_record = frappe.get_cached_doc("Examination", record.examination)
	return exam_record.get_questions_for_candidate()