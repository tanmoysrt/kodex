// Copyright (c) 2024, tanmoysrt and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Candidate Registration", {
	refresh(frm) {
		frm.add_custom_button(__("Grade Examination"), function(){
		    alert("Not implemented yet");
		});
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
		});
	},
});
