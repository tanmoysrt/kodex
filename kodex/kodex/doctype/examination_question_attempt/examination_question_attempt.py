# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import time

import frappe
from frappe.model.document import Document
from kodex.kodex.doctype.code_runner.code_runner import CodeRunner


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


	def question_type(self):
		return frappe.db.get_value("Question", self.question, "type")

	def grade_textual_question(self):
		if self.question_type() != "text":
			frappe.throw("Question is not of type text")
		frappe.throw("Textual question should be graded by the user")

	def grade_mcq(self):
		if self.question_type() != "mcq":
			frappe.throw("Question is not of type mcq")
		question = frappe.get_doc("Question", self.question)
		answer = self.submitted_answer
		marks = 0
		for c in question.mcq_question_choices:
			if c.option == answer:
				marking_percentage = c.partial_marking_percentage
				marks = question.marks * marking_percentage / 100
				break
		self.graded = True
		self.correct_answer = marks == question.marks
		self.marks = marks
		self.max_marks = question.marks
		self.save()

	def grade_coding_question_async(self):
		grader = frappe.new_doc("Coding Question Grader")
		grader.examination_question_attempt = self.name
		grader.save()

	def on_update(self):
		if self.graded:
			exam_record = frappe.get_doc("Examination Candidate Registration", self.examination_candidate_registration)
			exam_record.check_for_grading()

	@frappe.whitelist()
	def grade_as_correct(self):
		question = frappe.get_cached_doc("Question", self.question)
		self.graded = True
		self.correct_answer = True
		self.max_marks = question.marks
		self.marks = question.marks
		self.save()
		frappe.msgprint("Graded as correct", alert=True)

	@frappe.whitelist()
	def grade_as_incorrect(self):
		question = frappe.get_cached_doc("Question", self.question)
		self.graded = True
		self.correct_answer = False
		self.max_marks = question.marks
		self.marks = 0
		self.save()
		frappe.msgprint("Graded as incorrect", alert=True)

	@staticmethod
	def record(exam_candidate_registration_name, question_name, answer, language_id):
		# try to find out if with same qstn attempt exists
		try:
			r = frappe.get_doc("Examination Question Attempt", {
				"examination_candidate_registration": exam_candidate_registration_name,
				"question": question_name,
			})
			r.submitted_answer = answer
			r.language_id = language_id
			r.save(ignore_permissions=True)
		except Exception as e:
			r = frappe.new_doc("Examination Question Attempt")
			r.examination_candidate_registration = exam_candidate_registration_name
			r.question = question_name
			r.submitted_answer = answer
			r.language_id = language_id
			r.save(ignore_permissions=True)