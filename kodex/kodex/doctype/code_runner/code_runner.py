# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from kodex.utils import judge0
import base64

class CodeRunner(Document):
	def before_insert(self):
		self.access_token = frappe.generate_hash(length=20)
		submission_success, submission_token = judge0.submit_question(self.code, self.judge0_language_id, self.input)
		if submission_success:
			self.status = "submitted"
			self.judge0_submission_id = submission_token
		else:
			self.status = "failed"
			self.judge0_submission_id = ""

	@staticmethod
	def run_code(code, language_id, input) -> [str, str]:
		doc = frappe.new_doc("Code Runner")
		doc.code = code
		doc.input = input
		# check if language is available
		if not frappe.get_cached_doc("Coding Language", language_id):
			frappe.throw("Language not found")
		doc.judge0_language_id = language_id
		doc.save(ignore_permissions=True)
		return [doc.name, doc.access_token]

def check_code_submission_results():
	submitted_codes = frappe.get_list("Code Runner", fields=["name", "judge0_submission_id"], filters={"status": "submitted"})
	for code in submitted_codes:
		result_fetch_success, result = judge0.fetch_submission_result(code.judge0_submission_id)
		if result_fetch_success and result["status"] and result["status"]["id"] >= 3:
			doc = frappe.get_doc("Code Runner", code.name)
			if result["status"]["id"] == 3:
				doc.status = "completed"
				doc.output = (base64.b64decode(result["stdout"]).decode("utf-8") if result["stdout"] else "").rstrip()
				doc.error = (base64.b64decode(result["stderr"]).decode("utf-8") if result["stderr"] else "").rstrip()
				doc.compile_output = (base64.b64decode(result["compile_output"]).decode("utf-8") if result["compile_output"] else "").rstrip()
				doc.time_second = float(result["time"])
				doc.memory_kb = result["memory"]
				doc.debug_judge0_status_id = result["status"]["id"]
				doc.debug_judge0_status_description = result["status"]["description"]
			else:
				try:
					doc.status = "failed"
					doc.error = (base64.b64decode(result["stderr"]).decode("utf-8") if result["stderr"] else "").rstrip()
					doc.compile_output = (base64.b64decode(result["compile_output"]).decode("utf-8") if result["compile_output"] else "").rstrip()
					doc.debug_judge0_status_id = result["status"]["id"]
					doc.debug_judge0_status_description = (result["status"]["description"]).rstrip()
				except Exception as e:
					frappe.log_error("failed to update code runner status", message=e)
			doc.save(ignore_permissions=True)
