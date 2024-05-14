# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import datetime

import frappe
from frappe.model.document import Document


class ExaminationCandidateRegistration(Document):
	def validate(self):
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

	def after_insert(self):
		candidate_record = frappe.get_doc("User", self.candidate)
		examination_record = frappe.get_doc("Examination", self.examination)
		email_template = frappe.get_doc("Email Template", "Exam Registration Confirmation")
		email_args = {
			"candidate_name": candidate_record.name,
			"exam_name": examination_record.exam_name,
			"exam_duration": f"{self.login_window_minutes} minutes",
			"exam_start_time": frappe.utils.get_datetime(self.start_time).strftime("%d-%m-%Y %I:%M %p"),
			"exam_end_time": frappe.utils.get_datetime(self.end_time).strftime("%d-%m-%Y %I:%M %p"),
		}
		frappe.sendmail(
			recipients=[candidate_record.email],
			subject=email_template.get_formatted_subject(email_args),
			message=email_template.get_formatted_response(email_args),
			delayed=True
		)

	def send_invitation(self):
		pass
