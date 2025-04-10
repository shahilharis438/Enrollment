// Copyright (c) 2025, shahil and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Enrollment Details", {
    validate: function (frm) {
        //email validation
        const email_regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!email_regex.test(frm.doc.email)) {
            frappe.throw(__('Please enter a valid email address.'));
        }

        //date validation
        const today = frappe.datetime.str_to_obj(frappe.datetime.get_today());
        const enrollment_date = frappe.datetime.str_to_obj(frm.doc.enrollment_date);

        if (enrollment_date > today) {
            frappe.throw(__('Enrollment date cannot be in the future.'));
        }
    }
});
