import requests
import base64
import frappe

def submit_question(code, language_id, stdin) -> [bool, str]:
	try:
		judge0_base_url = frappe.get_cached_value("Kodex Settings", "Kodex Settings", "judge0_base_url")
		headers = {
			"Content-Type": "application/json",
		}
		data = {
			"source_code": base64.b64encode(code.encode("utf-8")).decode("utf-8"),
			"language_id": language_id,
			"stdin": base64.b64encode(stdin.encode("utf-8")).decode("utf-8") if stdin else "",
		}
		judge0_base_url = judge0_base_url.rstrip("/")
		response = requests.post(f"{judge0_base_url}/submissions/?base64_encoded=true&wait=false", headers=headers, json=data)
		if response.status_code != 201 or "token" not in response.json():
			frappe.log_error(f"Error submitting question to Judge0", message=response.json())
			return [False, ""]
		token = response.json()["token"]
		return [True, token]
	except Exception as e:
		frappe.log_error(f"Error submitting question to Judge0", message=e)
		return [False, ""]

def fetch_submission_result(token) -> [bool, dict]:
	try:
		judge0_base_url = frappe.get_cached_value("Kodex Settings", "Kodex Settings", "judge0_base_url")
		headers = {
			"Content-Type": "application/json",
		}
		judge0_base_url = judge0_base_url.rstrip("/")
		response = requests.get(f"{judge0_base_url}/submissions/{token}?base64_encoded=true&fields=stdout,stderr,time,memory,status,compile_output", headers=headers)
		if response.status_code != 200:
			return [False, {}]
		return [True, response.json()]
	except Exception as e:
		return [False, {}]