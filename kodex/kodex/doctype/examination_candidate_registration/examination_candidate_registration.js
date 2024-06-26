// Copyright (c) 2024, tanmoysrt and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Candidate Registration", {
	refresh(frm) {
		frm.add_custom_button(__("Send Invitation"), function(){
			frappe.call({
				method: "send_invitation",
				doc: frm.doc,
				args: {},
				freeze: true,
				freeze_message: __("Sending invitation..."),
				callback: function(r) {
					if (r.exc) {
						frappe.msgprint(r.exc);
					} else {
						frappe.msgprint(__("Invitation sent successfully"));
					}
				},
				error: function(r) {
					frappe.msgprint(r.message);
				}
			});
		}, __("Actions"));

		frm.add_custom_button(__("Grade Examination"), function(){
			frappe.call({
				method: "grade_exam",
				doc: frm.doc,
				args: {},
				freeze: true,
				freeze_message: __("Grading exam..."),
				callback: function(r) {
					if (r.exc) {
						frappe.msgprint(r.exc);
					} else {
						frappe.msgprint(r.message);
					}
				},
				error: function(r) {
					frappe.msgprint(r.message);
				}
			});
		}, __("Actions"));

		frm.add_custom_button(__("View Proctoring Images"), function(){
			window.open(frappe.urllib.get_full_url(`/app/exam-proctoring-images?id=${frm.doc.name}`), "_blank");
		}, __("Proctoring Images"));

		frm.add_custom_button(__("Delete Proctoring Images"), function(){
			frm.call("delete_proctoring_images")
		}, __("Proctoring Images"));
	},
});
