// Copyright (c) 2025, shahil and contributors
// For license information, please see license.txt

frappe.query_reports["Sale Tracker"] = {
	"filters": [
		{
			fieldname: "start_date",
			label: "Start Date",
			fieldtype: "Date",
			default: frappe.datetime.month_start(),  // optional: set default to month start
			reqd: 1
		},
		{
			fieldname: "end_date",
			label: "End Date",
			fieldtype: "Date",
			default: frappe.datetime.month_end(),    // optional: set default to month end
			reqd: 1
		}
	]
};
