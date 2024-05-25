// Copyright (c) 2024, tanmoysrt and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Question Attempt", {
	refresh(frm) {
    frm.add_custom_button(__("Grade as correct"), () => {
      frm.call("grade_as_correct");
    }, __("Grade Actions"));
    frm.add_custom_button(__("Grade as incorrect"), () => {
      frm.call("grade_as_incorrect");
    }, __("Grade Actions"));
	},
});
