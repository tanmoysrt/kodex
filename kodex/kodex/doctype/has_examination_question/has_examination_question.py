# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class HasExaminationQuestion(Document):
	def validate(self):
		if frappe.db.exists("Examination Question Mapping",
		                    {"examination": self.examination, "question": self.question}):
			frappe.throw("Examination Question Mapping already exists")