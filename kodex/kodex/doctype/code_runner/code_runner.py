# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from kodex.utils import judge0
import base64
import time

class CodeRunner(Document):
	def before_insert(self):
		submission_success, submission_token = judge0.submit_question(self.code, self.judge0_language_id, self.input)
		if submission_success:
			self.status = "submitted"
			self.judge0_submission_id = submission_token
		else:
			self.status = "failed"
			self.judge0_submission_id = ""

def check_code_submission_results():
	submitted_codes = frappe.get_list("Code Runner", fields=["name", "judge0_submission_id"], filters={"status": "submitted"})
	for code in submitted_codes:
		result_fetch_success, result = judge0.fetch_submission_result(code.judge0_submission_id)
		if result_fetch_success and result["status"] and result["status"]["id"] >= 3:
			doc = frappe.get_doc("Code Runner", code.name)
			if result["status"]["id"] == 3:
				doc.status = "completed"
				doc.output = base64.b64decode(result["stdout"]).decode("utf-8") if result["stdout"] else ""
				doc.error = base64.b64decode(result["stderr"]).decode("utf-8") if result["stderr"] else ""
				doc.compile_output = base64.b64decode(result["compile_output"]).decode("utf-8") if result["compile_output"] else ""
				doc.time_second = float(result["time"])
				doc.memory_kb = result["memory"]
				doc.debug_judge0_status_id = result["status"]["id"]
				doc.debug_judge0_status_description = result["status"]["description"]
			else:
				doc.status = "failed"
				doc.error = base64.b64decode(result["stderr"]).decode("utf-8") if result["stderr"] else ""
				doc.compile_output = base64.b64decode(result["compile_output"]).decode("utf-8") if result["compile_output"] else ""
				doc.debug_judge0_status_id = result["status"]["id"]
				doc.debug_judge0_status_description = result["status"]["description"]
			doc.save()
