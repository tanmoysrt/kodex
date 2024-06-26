# Copyright (c) 2024, tanmoysrt and contributors
# For license information, please see license.txt
import base64
import datetime
import json

import frappe
from frappe.model.document import Document


class ExaminationCandidateRegistration(Document):
    @property
    def exam_url(self):
        payload = {"name": self.name, "auth_token": self.auth_token}
        payload_base64 = base64.b64encode(json.dumps(payload).encode("utf-8")).decode(
            "utf-8"
        )
        return f"{frappe.utils.get_url()}/kodex/{payload_base64}"

    @property
    def percentage(self):
        if self.total_marks is None or self.gained_marks is None:
            return 0
        if self.total_marks == 0:
            return 0
        return (self.gained_marks / self.total_marks) * 100

    def before_save(self):
        if not self.auth_token:
            self.auth_token = frappe.generate_hash(length=64)

    def after_insert(self):
        kodex_settings = frappe.get_single("Kodex Settings")
        if kodex_settings.send_email_on_exam_registration:
            self.send_invitation()

    @frappe.whitelist()
    def send_invitation(self):
        frappe.enqueue_doc(
            "Examination Candidate Registration", self.name, method="_send_invitation"
        )
        frappe.msgprint("Exam invitation e-mail will be send soon.")

    def _send_invitation(self):
        examination_record = frappe.get_doc("Examination", self.examination)
        email_template = frappe.get_doc(
            "Email Template", "Exam Registration Confirmation"
        )
        email_args = {
            "candidate_name": self.candidate_name,
            "exam_name": examination_record.exam_name,
            "exam_duration": f"{self.login_window_minutes} minutes",
            "exam_start_time": frappe.utils.get_datetime(self.start_time).strftime(
                "%d-%m-%Y %I:%M %p"
            ),
            "exam_end_time": frappe.utils.get_datetime(self.end_time).strftime(
                "%d-%m-%Y %I:%M %p"
            ),
            "exam_url": self.exam_url,
        }
        frappe.sendmail(
            recipients=[self.candidate_email_id],
            subject=email_template.get_formatted_subject(email_args),
            message=email_template.get_formatted_response(email_args),
            delayed=False,
        )

    def start_exam(self):
        if not self.exam_started_on:
            self.exam_started_on = frappe.utils.get_datetime()
            self.save(ignore_permissions=True)

    def end_exam(self):
        if not self.exam_started_on:
            self.exam_started_on = frappe.utils.get_datetime()
        self.exam_ended = True
        self.exam_ended_on = frappe.utils.get_datetime()
        self.save(ignore_permissions=True)
        self.send_exam_submission_email()

    def end_exam_due_to_malpractice(self, reason):
        if not self.exam_started_on:
            self.exam_started_on = frappe.utils.get_datetime()
        self.exam_ended = True
        self.exam_ended_on = frappe.utils.get_datetime()
        self.ended_due_to_malpractice = True
        self.malpractice_info = reason
        self.save(ignore_permissions=True)
        self.send_exam_submission_email()

    def send_exam_submission_email(self):
        frappe.enqueue_doc(
            "Examination Candidate Registration",
            self.name,
            method="_send_exam_submission_email",
        )

    def _send_exam_submission_email(self):
        kodex_settings = frappe.get_single("Kodex Settings")
        if kodex_settings.send_email_on_exam_submission:
            examination_record = frappe.get_doc("Examination", self.examination)
            email_template = frappe.get_doc(
                "Email Template", "Exam Submission Confirmation"
            )
            email_args = {
                "candidate_name": self.candidate_name,
                "exam_name": examination_record.exam_name,
            }
            frappe.sendmail(
                recipients=[self.candidate_email_id],
                subject=email_template.get_formatted_subject(email_args),
                message=email_template.get_formatted_response(email_args),
                delayed=False,
            )

    def check_auth(self, auth_token):
        if auth_token != self.auth_token:
            frappe.throw("Invalid Auth Token")

    def is_exam_started(self):
        return self.exam_started_on is not None

    def validate_for_starting_exam(self) -> [bool, str]:
        # check if exam has not ended
        if self.exam_ended:
            return [False, "Candidate has already submitted the exam"]
        # check if current time is between start time and end time
        if frappe.utils.get_datetime() < self.start_time:
            return [False, "Exam has not started yet\nRefresh the page to check again"]
        if frappe.utils.get_datetime() > self.end_time:
            return [False, "Exam window has expired"]
        # check if exam is started and start time + login window is not passed
        if self.exam_started_on:
            if (
                frappe.utils.get_datetime(self.exam_started_on)
                + datetime.timedelta(minutes=self.login_window_minutes)
                < frappe.utils.get_datetime()
            ):
                return [False, "Candidate has already submitted the exam"]
        return [True, "you are good to start the exam"]

    @frappe.whitelist()
    def grade_exam(self):
        question_attempts_name = frappe.get_list(
            "Examination Question Attempt",
            filters={"examination_candidate_registration": self.name},
            fields=["name"],
        )
        question_attempts_record = [
            frappe.get_doc("Examination Question Attempt", x.name)
            for x in question_attempts_name
        ]

        # Check textual questions
        non_gradable_questions = []
        for record in question_attempts_record:
            if not record.graded and record.question_type() == "text":
                non_gradable_questions.append(record.question)
        if len(non_gradable_questions) > 0:
            frappe.msgprint(
                non_gradable_questions,
                title="Textual questions can't be graded",
                as_list=True,
            )
            return

        # Check MCQ questions
        mcq_questions_count = 0
        for record in question_attempts_record:
            if record.question_type() == "mcq":
                mcq_questions_count += 1

        # Check coding questions
        coding_questions_count = 0
        for record in question_attempts_record:
            if record.question_type() == "coding":
                coding_questions_count += 1

        if mcq_questions_count > 0 or coding_questions_count > 0:
            frappe.msgprint(
                f"Graded {mcq_questions_count} MCQ questions and {coding_questions_count} coding questions enqueued for grading"
            )
            # set status
            self.grading_status = "grading"
            self.save()
            self.grade_questions()
        else:
            frappe.msgprint("No Question Attempts found to grade")

    def grade_questions(self):
        frappe.enqueue_doc("Examination Candidate Registration", self.name, method="_grade_questions")

    def _grade_questions(self):
        question_attempts_name = frappe.get_list(
            "Examination Question Attempt",
            filters={"examination_candidate_registration": self.name},
            fields=["name"],
        )
        question_attempts_record = [
            frappe.get_doc("Examination Question Attempt", x.name)
            for x in question_attempts_name
        ]
        # Check MCQ questions
        for record in question_attempts_record:
            if record.question_type() == "mcq":
                record.grade_mcq()

        # Check coding questions
        for record in question_attempts_record:
            if record.question_type() == "coding":
                record.grade_coding_question_async()

    def check_for_grading(self):
        pending_questions_for_grading_count = frappe.db.count(
            "Examination Question Attempt",
            {"examination_candidate_registration": self.name, "graded": False},
        )
        if pending_questions_for_grading_count > 0:
            return
        question_attempt = frappe.qb.DocType("Examination Question Attempt")
        sum_marks = frappe.qb.functions("SUM", question_attempt.marks).as_("sum_marks")
        result = (
            frappe.qb.from_(question_attempt)
            .where(question_attempt.examination_candidate_registration == self.name)
            .select(sum_marks)
            .run(as_dict=True)
        )
        self.gained_marks = result[0]["sum_marks"]
        self.total_marks = frappe.get_doc("Examination", self.examination).total_marks
        self.grading_status = "graded"
        self.save()

    @frappe.whitelist()
    def delete_proctoring_images(self):
        files = frappe.get_list(
            "File",
            {
                "attached_to_doctype": "Examination Candidate Registration",
                "attached_to_name": self.name,
            },
            pluck="name",
        )
        for file in files:
            frappe.delete_doc("File", file)
        frappe.msgprint(f"Deleted {len(files)} proctoring images", alert=True)


@frappe.whitelist()
def get_proctoring_images(exam_candidate_registration_name):
    return frappe.get_list(
        "File",
        {
            "attached_to_doctype": "Examination Candidate Registration",
            "attached_to_name": exam_candidate_registration_name,
        },
        pluck="file_url",
    )


def auto_submit_running_exams():
    """
    Auto submit exams if after exam, user has not submitted and the exam is over in meantime
    """
    try:
        running_exams = frappe.get_list(
            "Examination Candidate Registration",
            filters={
                "exam_started_on": ["is", "set"],
                "exam_ended_on": ["is", "not set"],
            },
            fields=["name", "exam_started_on", "login_window_minutes"],
        )
        for exam in running_exams:
            if frappe.utils.get_datetime() >= frappe.utils.get_datetime(
                exam.exam_started_on
            ) + datetime.timedelta(minutes=exam.login_window_minutes):
                exam_record = frappe.get_doc(
                    "Examination Candidate Registration", exam.name
                )
                exam_record.end_exam()
    except Exception as e:
        frappe.log_error(f"Error auto submitting running exams", message=e)
