# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import base64
import datetime
import json

import frappe
from frappe.model.document import Document


class ExaminationCandidateRegistration(Document):
	@property
	def exam_url(self):
		payload = {
			"name": self.name,
			"auth_token": self.auth_token
		}
		payload_base64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")
		return f"{frappe.utils.get_url()}/exam/{payload_base64}"

	def validate(self):
		if self.is_new():
			# check if no duplicate candidate is registered
			if frappe.db.exists("Examination Candidate Registration",
			                    {"candidate": self.candidate, "examination": self.examination}):
				frappe.throw("Candidate is already registered")

	def before_save(self):
		# Check if "Examination Candidate" role is exist in the user roles
		candidate_record = frappe.get_doc("User", self.candidate)
		isRoleFound = False
		for record in candidate_record.roles:
			if record.role == "Examination Candidate":
				isRoleFound = True
				break
		if not isRoleFound:
			candidate_record.append('roles', {
				"doctype": "Has Role",
				"role": "Examination Candidate"
			})
			candidate_record.save()
		if not self.auth_token:
			self.auth_token = frappe.generate_hash(length=64)

	def after_insert(self):
		self.send_invitation()

	@frappe.whitelist()
	def send_invitation(self):
		candidate_record = frappe.get_doc("User", self.candidate)
		examination_record = frappe.get_doc("Examination", self.examination)
		email_template = frappe.get_doc("Email Template", "Exam Registration Confirmation")
		email_args = {
			"candidate_name": candidate_record.first_name,
			"exam_name": examination_record.exam_name,
			"exam_duration": f"{self.login_window_minutes} minutes",
			"exam_start_time": frappe.utils.get_datetime(self.start_time).strftime("%d-%m-%Y %I:%M %p"),
			"exam_end_time": frappe.utils.get_datetime(self.end_time).strftime("%d-%m-%Y %I:%M %p"),
			"exam_url": self.exam_url
		}
		frappe.sendmail(
			recipients=[candidate_record.email],
			subject=email_template.get_formatted_subject(email_args),
			message=email_template.get_formatted_response(email_args),
			delayed=False
		)

	def start_exam(self):
		if not self.exam_started_on:
			self.exam_started_on = frappe.utils.get_datetime()
			self.save(ignore_permissions=True)

	def end_exam(self):
		if not self.exam_started_on:
			self.exam_started_on = frappe.utils.get_datetime()
		self.exam_ended = True
		self.exam_ended_on = frappe.utils.get_datetime()
		self.save(ignore_permissions=True)

	def end_exam_due_to_malpractice(self, reason):
		if not self.exam_started_on:
			self.exam_started_on = frappe.utils.get_datetime()
		self.exam_ended = True
		self.exam_ended_on = frappe.utils.get_datetime()
		self.ended_due_to_malpractice = True
		self.malpractice_info = reason
		self.save(ignore_permissions=True)

	def check_auth(self, auth_token):
		if auth_token != self.auth_token:
			frappe.throw("Invalid Auth Token")

	def is_exam_started(self):
		return self.exam_started_on is not None

	def validate_for_starting_exam(self) -> [bool, str]:
		# check if exam has not ended
		if self.exam_ended:
			return [False, "Candidate has already submitted the exam"]
		# check if current time is between start time and end time
		if frappe.utils.get_datetime() < self.start_time:
			return [False, "Exam has not started yet\nRefresh the page to check again"]
		if frappe.utils.get_datetime() > self.end_time:
			return [False, "Exam window has expired"]
		# check if exam is started and start time + login window is not passed
		if self.exam_started_on:
			if frappe.utils.get_datetime(self.exam_started_on) + datetime.timedelta(
					minutes=self.login_window_minutes) < frappe.utils.get_datetime():
				return [False, "Candidate has already submitted the exam"]
		return [True, "you are good to go"]


@frappe.whitelist()
def get_proctoring_images(exam_candidate_registration_name):
	return frappe.get_list("File", {
		"attached_to_doctype": "Examination Candidate Registration",
		"attached_to_name": exam_candidate_registration_name
	}, pluck="file_url")
