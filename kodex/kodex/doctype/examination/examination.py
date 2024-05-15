# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import frappe
# import frappe
from frappe.model.document import Document


class Examination(Document):
	@property
	def total_questions(self):
		return len(self.questions)

	@property
	def total_marks(self):
		return sum(frappe.get_list("Question", filters=[["name", "in", [record.question for record in self.questions]]], pluck="marks", ignore_permissions=True))

	def get_questions_for_candidate(self):
		"""
		Hide sensitive information from the question doctype
		Send only the info related to the question
		"""
		questions_names = [record.question for record in self.questions]
		questions_data = []
		for question in questions_names:
			question_data = frappe.get_cached_doc("Question", question)
			questions_data.append({
				"name": question,
				"description": question_data.description,
				"type": question_data.type,
				"marks": question_data.marks,
				"mcq_question_choices": [x.option for x in  question_data.mcq_question_choices],
				"coding_question": {
					"available_languages": [{
						"title": frappe.get_cached_value("Coding Language",x.language,"title"),
						"id": x.language
					} for x in question_data.available_languages],
					"test_cases": [{
						"input": x.input,
						"output": x.output,
					} for x in question_data.code_question_testset if not x.hidden]
				}
			})
		return questions_data