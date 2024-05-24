# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import time

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

	@frappe.whitelist()
	def grade(self) -> bool:
		if self.graded:
			return True
		question = frappe.get_cached_doc("Question", self.question)
		answer = self.submitted_answer
		is_correct = False
		marks = 0
		if question.type == "mcq":
			marking_percentage = 0
			for c in question.mcq_question_choices:
				if c.option == answer:
					marking_percentage = c.partial_marking_percentage
					marks = question.marks * marking_percentage / 100
					break
			is_correct = marking_percentage == 100
		elif question.type == "text":
			return False
		elif question.type == "coding":
			# Run the codes
			test_cases = question.code_question_testset
			# TODO fix this
			# Try to fetch result each 3 seconds until unless it's failed/completed
			pass

		self.graded = True
		self.correct_answer = is_correct
		self.marks = marks
		self.save()
		return True

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