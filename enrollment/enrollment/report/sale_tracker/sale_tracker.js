// Copyright (c) 2025, shahil and contributors
// For license information, please see license.txt

frappe.query_reports["Sale Tracker"] = {
	"filters": [
		{
			fieldname: "start_date",
			label: "Start Date",
			fieldtype: "Date",
			default: frappe.datetime.month_start(),
			reqd: 1
		},
		{
			fieldname: "end_date",
			label: "End Date",
			fieldtype: "Date",
			default: frappe.datetime.month_end(),
			reqd: 1
		},
		{
			fieldname: "sales_person",
			label: "Academic Councelor",
			fieldtype: "Link",
			options: "Sales Person",
		},
		{
			fieldname: "product",
			label: "Product",
			fieldtype: "Link",
			options: "Product",
		},
	],

	onload: function (report) {
		// Add button to redirect to another report

		const wrapper = report.page.main;
		$(wrapper).append('<div id="extra-chart" style="margin-top: 40px;"></div>');

		
		frappe.call({
			method: "enrollment.enrollment.report.sale_tracker.sale_tracker.get_second_chart",  
			args: {
				filters: report.get_filter_values()
			},
			callback: function (r) {
				if (r.message) {
					new frappe.Chart("#extra-chart", r.message);
				}
			}
		});
	}
};
