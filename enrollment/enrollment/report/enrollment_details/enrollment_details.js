// Copyright (c) 2025, shahil and contributors
// For license information, please see license.txt

frappe.query_reports["Enrollment Details"] = {
	filters: [
		{
			fieldname: "date_from",
			label: "From Date",
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
		},
		{
			fieldname: "date_to",
			label: "To Date",
			fieldtype: "Date",
			default: frappe.datetime.get_today()
		},

	]
};