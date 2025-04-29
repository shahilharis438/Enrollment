# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import getdate, add_days
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count
from datetime import datetime


months_num = {
    1: "january",2: "february",3: "march",4: "april",
    5: "may",6: "june",7: "july",8: "august",
    9: "september",10: "october",11: "november",12: "december"
    }
sa = DocType("Sales Activity")
sp = DocType("Sales Person")
spt = DocType("Sales Person Target")
mt = DocType("Monthly Target")

@frappe.whitelist()
def execute(start_date, end_date, sales_person, product):
	data = []
	days = []
	columns = [
		{"label": "Academic Counselor", "fieldname": "acad_coun", "fieldtype": "Link", "options": "Sales Person", "width": 200},
		{"label": "Progress", "fieldname": "progress", "fieldtype": "Data", "width": 180},
		{"label": "SFR", "fieldname": "sfr", "fieldtype": "Data", "width": 120},
		{"label": "TARGET SFR", "fieldname": "target_sfr", "fieldtype": "Data", "width": 200},
		{"label": "SFR Percentage", "fieldname": "sfr_perc", "fieldtype": "Data", "width": 200},
		{"label": "ADMS", "fieldname": "adms", "fieldtype": "Data", "width": 100},
		{"label": "Sales Amount", "fieldname": "total_sale_value", "fieldtype": "Currency", "width": 200},
		{"label": "Sales Collection", "fieldname": "sales_collection", "fieldtype": "Currency", "width": 200},
		{"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 200},
		{"label": "Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 200},
		{"label": "Product", "fieldname": "product", "fieldtype": "Link", "options": "Product", "width": 200},
		{"label": "Target Percentage", "fieldname": "target_perc", "fieldtype": "Data", "width": 200},
		{"label": "ARPU", "fieldname": "arpu", "fieldtype": "Data", "width": 200},
		{"label": "ACR", "fieldname": "acr", "fieldtype": "Data", "width": 200},
		{"label": "Installment", "fieldname": "installment", "fieldtype": "Data", "width": 200},
		{"label": "Installment Collection", "fieldname": "installment_collection", "fieldtype": "Currency", "width": 200},
		{"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 200},
	]
	

	
	date_field = {}
	col_data = {}
	if  start_date and end_date:
		date_field = set_dates(start_date, end_date, columns)
		month = datetime.strptime(str(start_date), "%Y-%m-%d").month
		
		main_query = (
		    frappe.qb
		    .from_(sa)
		    .join(sp).on(sa.sales_person == sp.sales_person_name)
		    .left_join(spt).on(spt.sales_person == sa.sales_person)
            .left_join(mt).on(mt.parent == spt.name)
		    .select(
			        sa.sales_person.as_("acad_coun"),
			        Sum(sa.total_sale_value).as_("total_sale_value"),
			        Sum(sa.amount_paid).as_("sales_collection"),
			        mt.target,
			        sa.outstanding_amount.as_("outstanding"),
			        Sum(sa.connected_calls).as_("sfr"),
			        Count(sa.name).as_("adms"),
			        mt.target_sfr,
			        sa.course_purchased.as_("product")
		    )
		    .where((sa.date_of_sale >= start_date) & (sa.date_of_sale <= end_date))
            .where(months_num[month] == mt.month)
		    .groupby(sa.sales_person)
        )
    
   
		if sales_person:
			main_query = main_query.where(sa.sales_person == sales_person)
		if product:
			main_query = main_query.where(sa.course_purchased == product)

		main_query = main_query.run(as_dict=1)
   
		if main_query:
			for row in main_query:
			
				sales_collection = row.get("sales_collection") or 0
				total_sale_value = row.get("total_sale_value") or 0
				adms = row.get("adms") or 0
				sfr = row.get("sfr") or 0
				target = row.get("target") if row.get("target") else 0
				target_sfr =  int(row.get("target_sfr")) if row.get("target_sfr") else 0
        
       
				row["target_perc"] = (round(sales_collection / target * 100, 2)) if target else 0
				row["progress"] = (round(total_sale_value / target * 100, 2)) if target else 0
				row["sfr_perc"] = (round((sfr / target_sfr) * 100, 2)) if target_sfr else 0
				row["acr"] = (round(adms / sfr, 3)) if sfr else 0
				row["arpu"] = (round(sales_collection / adms, 2)) if adms else 0
        
				result = frappe.db.get_all(
			    	"Sales Activity",
			    	filters={
						"sales_person": row["acad_coun"],
						"types_of_report": "Installment"
			    	},
			    	fields=[
				    	"COUNT(name) as installment",
				    	"SUM(amount_paid) as installment_collection"
			    	]
		   	 	)

				row["installment"] = result[0].installment or 0
				row["installment_collection"] = result[0].installment_collection or 0

				daywise_query = (
			    	frappe.qb
			    	.from_(sa)
			    	.select(sa.date_of_sale, Sum(sa.amount_paid).as_("amount_paid"))
			    	.where(
					(sa.date_of_sale >= start_date) &
					(sa.date_of_sale <= end_date) &
					(sa.sales_person == row["acad_coun"])
			    	)
			    	.groupby(sa.date_of_sale)
			    	.run(as_dict=1)
		    	)
			
				for day_row in daywise_query:
					date_key = day_row.get("date_of_sale")
					if date_key and date_key in date_field:
						row[date_field[date_key]] = day_row.get("amount_paid") or 0
			
				data.append(row)
	
		for row in main_query:
			current_date_row = getdate(start_date)
			col_data = {} 
			while current_date_row <= getdate(end_date):
				label = current_date_row.strftime("%B %-d")
				col_data[label] = row.get(date_field.get(current_date_row)) or 0
				current_date_row = add_days(current_date_row, 1)
			row.update(col_data)
	
		for col in columns[17:]:
			days.append(col['label'])
	
	
	return data, days


@frappe.whitelist()
def get_sales_champions(start_date, end_date):
	
	month = datetime.strptime(str(start_date), "%Y-%m-%d").month
	labels_1, data_1, labels_2, data_2 = [], [], [], []
	chart_data = (
        frappe.qb.from_(sa)
        .left_join(spt).on(sa.sales_person == spt.sales_person)
		.left_join(mt).on(mt.parent == spt.name)
        .select(mt.target, sa.sales_person, Sum(sa.total_sale_value).as_("total_sale_value"),  
				Count(sa.name).as_("admission"), Sum(sa.connected_calls).as_("sfr"))
		.where((sa.date_of_sale >= start_date) & (sa.date_of_sale <=end_date) )
		.where(months_num[month] == mt.month)
        .groupby(sa.sales_person)
		.orderby("total_sale_value", desc=True)
		.run(as_dict=1)
        
    )
	
	
	for row in chart_data:
		labels_1.append(row.sales_person)
		perc = (row.total_sale_value / row.target) * 100
		data_1.append(perc)
		row['perc'] = perc
		row['conversion'] = (row["admission"] / row["sfr"])*100 if row["sfr"] !=0 else 0
	
	target_crusher_detail = max(chart_data, key=lambda x: x["total_sale_value"])
	coversion_pro_detail = max(chart_data, key=lambda x: x["conversion"])
	admission_star = max(chart_data, key=lambda x: x["admission"])
	
	labels_2.append(target_crusher_detail["sales_person"]+ " "+ "Target Crusher")
	labels_2.append(coversion_pro_detail["sales_person"]+ " "+ "Conversion Pro")
	labels_2.append(admission_star["sales_person"]+ " "+ "Admission Star")
	
	data_2.append(target_crusher_detail['perc'])
	data_2.append(coversion_pro_detail['conversion'])
	data_2.append(admission_star['admission'])
	
	return labels_1, data_1, labels_2, data_2


@frappe.whitelist()
def sfr_tracker(start_date, end_date, sales_person, product):
	columns = [{}]
	date_field = {}
	days = []
	data = []
	month = datetime.strptime(str(start_date), "%Y-%m-%d").month
	sfr_data = (
		frappe.qb.from_(sa)
		.left_join(spt).on(sa.sales_person == spt.sales_person)
		.left_join(mt).on(mt.parent == spt.name)
		.select(sa.sales_person, Sum(sa.total_sale_value).as_("sale_value"), mt.target, mt.target_sfr,  Sum(sa.connected_calls).as_("sfr"))
		.groupby(sa.sales_person)
		.where((sa.date_of_sale>= start_date) & (sa.date_of_sale<= end_date))
		.where(months_num[month] == mt.month)
		
		
	)
	
	if  start_date and end_date:
		date_field = set_dates(start_date, end_date, columns)
		if sales_person:
			sfr_data =sfr_data.where(sa.sales_person == sales_person)
		sfr_data = sfr_data.run(as_dict=1)
		sfr_sorted_data = sorted(sfr_data, key=lambda x: x['sfr'], reverse=True)
		for row in sfr_sorted_data:#query sorted sfr in desc order
			row['progress'] = round((row['sale_value'] / row['target'] * 100), 2)
			row['sfr_perc'] = round((row['sfr'] / int(row['target_sfr'])) * 100, 2)
			
			daywise_query = (
			    	frappe.qb
			    	.from_(sa)
			    	.select(sa.date_of_sale, Sum(sa.connected_calls).as_("connected_calls"))
			    	.where(
					(sa.date_of_sale >= start_date) &
					(sa.date_of_sale <= end_date) &
					(sa.sales_person == row["sales_person"])
			    	)
			    	.groupby(sa.date_of_sale)
			    	.run(as_dict=1)
		    	)
			leave_per_person = 0
			for day_row in daywise_query:
					date_key = day_row.get("date_of_sale")
					if date_key and date_key in date_field:
						employee = frappe.db.get_value("Sales Person", {'name': row["sales_person"]}, "employee")

						status = frappe.db.get_value("Attendance", {'employee': employee, "attendance_date": date_key}, "status")
						
						if status == "On Leave" or status == "Absent":
							leave_per_person += 1
							row[date_field[date_key]] = "L"
						else:
							row[date_field[date_key]] = day_row.get("connected_calls") or 0
			row.update({'leave': leave_per_person})
			data.append(row)
		
		for row in sfr_data:
			current_date_row = getdate(start_date)
			col_data = {} 
			while current_date_row <= getdate(end_date):
				label = current_date_row.strftime("%B %-d")
				col_data[label] = row.get(date_field.get(current_date_row)) or 0
				current_date_row = add_days(current_date_row, 1)
			row.update(col_data)
		
		rank = 1
		previous_sfr = None
		for idx, row in enumerate(sfr_sorted_data):
			if row['sfr'] != previous_sfr:
				rank = idx + 1
				previous_sfr = row['sfr']
			row['rank'] = rank
		
		for col in columns:
			if col:
				days.append(col['label'])

	return data, days

def set_dates(start_date, end_date, columns):
	start_date = getdate(start_date)
	end_date = getdate(end_date)
	date_field = {}	
	current_date = start_date
	
	
	while current_date <= end_date:
		label = current_date.strftime("%B %-d")
		fieldname = f"day_{current_date.strftime('%Y_%m_%d')}"
		date_field[current_date] = fieldname
		columns.append({
			"label": label,
			"fieldname": fieldname,
			"fieldtype": "Currency",
			"width": 120
		})
		current_date = add_days(current_date, 1)
	return date_field