# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ExaminationQuestionAttempt(Document):
	def validate(self):
		record = frappe.get_cached_doc("Examination Candidate Registration", self.examination_candidate_registration)
		if not record:
			frappe.throw("Examination Candidate Registration not found")
		if not record.is_exam_started():
			frappe.throw("Exam has not started yet")
		exam_record = frappe.get_cached_doc("Examination", record.examination)
		if self.question not in [x.question for x in exam_record.questions]:
			frappe.throw("Question not found")
		if self.submitted_answer == "":
			frappe.throw("Answer cannot be empty")

	@staticmethod
	def record(exam_candidate_registration_name, question_name, answer):
		# try to find out if with same qstn attempt exists
		try:
			r = frappe.get_doc("Examination Question Attempt", {
				"examination_candidate_registration": exam_candidate_registration_name,
				"question": question_name
			})
			r.submitted_answer = answer
			r.save(ignore_permissions=True)
		except Exception as e:
			r = frappe.new_doc("Examination Question Attempt")
			r.examination_candidate_registration = exam_candidate_registration_name
			r.question = question_name
			r.submitted_answer = answer
			r.save(ignore_permissions=True)