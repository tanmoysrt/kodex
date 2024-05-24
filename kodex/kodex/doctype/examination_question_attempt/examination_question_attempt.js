// Copyright (c) 2024, tanmoysrt and contributors
// For license information, please see license.txt

frappe.ui.form.on("Examination Question Attempt", {
	refresh(frm) {
    frm.add_custom_button(__("Grade test"), () => {
      frm.call("grade");
    });
	},
});
