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
			language_id = self.language_id
			if not language_id:
				is_correct = False
			elif not self.submitted_answer:
				is_correct = False
			else:
				test_cases = question.code_question_testset
				code_runner_records = {}
				for i in test_cases:
					response = CodeRunner.run_code(self.submitted_answer, language_id, i.input)
					code_runner_records[response[0]] = {
						"expected_output": i.output,
						"already_run": False,
						"is_correct": False,
					}
				frappe.db.commit()

				is_result_decided = False
				code_runner_dumps = {}
				while not is_result_decided:
					time.sleep(1)
					is_all_skipped = True
					for r in code_runner_records:
						if code_runner_records[r]["already_run"]:
							continue
						if r in code_runner_dumps:
							result = code_runner_dumps[r]
							result.reload()
						else:
							result = frappe.get_doc("Code Runner", r)
							code_runner_dumps[r] = result
						if result.status == "completed":
							code_runner_records[r]["is_correct"] = result.output == code_runner_records[r]["expected_output"]
							code_runner_records[r]["already_run"] = True
							is_all_skipped = False
						elif result.status == "failed":
							code_runner_records[r]["is_correct"] = False
							is_result_decided = True
							is_all_skipped = False
							break
						else:
							is_all_skipped = False
					if is_all_skipped:
						break

				# calculate marks
				is_correct = True
				for r in code_runner_records:
					is_correct = is_correct and code_runner_records[r]["is_correct"]

				if is_correct:
					marks = question.marks

		self.graded = True
		self.correct_answer = is_correct
		self.marks = marks
		self.max_marks = question.marks
		self.save()
		frappe.db.commit()
		return True

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