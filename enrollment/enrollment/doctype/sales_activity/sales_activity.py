# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesActivity(Document):
	def before_save(self):
		missing = []
		if self.types_of_report == "EOD":
			if not self.connected_calls:
				missing.append("connected calls")
			if not self.no_of_deals:
				missing.append("no of deals")
			if not self.converted_amount:
				missing.append("converted amount")
			if not self.call_time:
				missing.append("call time")
			if not self.interested:
				missing.append("interested")
			
		elif self.types_of_report == "New Sales" or self.types_of_report == "Installment":
			if not self.amount_paid:
				missing.append("amount paid")
			if not self.program_purchased:
				missing.append("program purchased")
			if not self.date_of_sale:
				missing.append("date_of_sale")
			if not self.payment_type:
				missing.append("payment type")
		if missing:
			frappe.throw(str(missing)+" fields are missing")
		missing = []



