# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from kodex.kodex.doctype.code_runner.code_runner import CodeRunner


class CodingQuestionGrader(Document):
	@property
	def total_testcases_count(self):
		return frappe.db.count("Code Runner", {
			"coding_question_grader": self.name
		})

	@property
	def successful_testcases_count(self):
		return frappe.db.count("Code Runner", {
			"coding_question_grader": self.name,
			"status": ["!=", "submitted"],
			"correct": True
		})

	@property
	def failed_testcases_count(self):
		return frappe.db.count("Code Runner", {
			"coding_question_grader": self.name,
			"status": ["!=", "submitted"],
			"correct": False
		})


	def after_insert(self):
		question_attempt = frappe.get_doc("Examination Question Attempt", self.examination_question_attempt)
		question = frappe.get_doc("Question", question_attempt.question)
		if question.type == "coding":
			testsets = question.code_question_testset
			self.save()
			for test in testsets:
				CodeRunner.run_code_for_grading(question_attempt.submitted_answer,question_attempt.language_id, test.input, test.output, self.name)

	def check_grading_completion(self):
		if self.total_testcases_count == self.successful_testcases_count + self.failed_testcases_count:
			examination_question_attempt = frappe.get_doc("Examination Question Attempt", self.examination_question_attempt)
			examination_question_attempt.graded = True
			examination_question_attempt.correct_answer = self.successful_testcases_count == self.total_testcases_count
			if examination_question_attempt.correct_answer:
				question_marks = frappe.db.get_value("Question", examination_question_attempt.question, "marks")
				examination_question_attempt.marks = question_marks
				examination_question_attempt.max_marks = question_marks
			else:
				examination_question_attempt.marks = 0
				examination_question_attempt.max_marks = 0
			examination_question_attempt.save()