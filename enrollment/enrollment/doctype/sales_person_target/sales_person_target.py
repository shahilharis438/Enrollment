# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesPersonTarget(Document):
	def before_save(self):
		month = self.custom_monthly_target_amount[0].get("month")
		for row in self.custom_monthly_target_amount[1:]:
			if row.get('month') == month:
				frappe.throw("Months must not be repeated")
