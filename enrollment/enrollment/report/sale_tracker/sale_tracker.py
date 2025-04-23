# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt
import frappe
from frappe.utils import getdate, add_days
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count

def execute(filters=None):
    data = []
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

    sa = DocType("Sales Activity")
    sp = DocType("Sales Person")
    spt = DocType("Sales Person Target")

    date_field = {}

    if filters and filters.get("start_date") and filters.get("end_date"):
        start_date = getdate(filters.get("start_date"))
        end_date = getdate(filters.get("end_date"))

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

    main_query = (
		frappe.qb
		.from_(sa)
		.join(sp).on(sa.sales_person == sp.sales_person_name)
		.join(spt).on(spt.sales_person == sa.sales_person)
		.select(
			sa.sales_person.as_("acad_coun"),
			Sum(sa.total_sale_value).as_("total_sale_value"),
			Sum(sa.amount_paid).as_("sales_collection"),
			spt.target.as_("target"),
			sa.outstanding_amount.as_("outstanding"),
			Sum(sa.connected_calls).as_("sfr"),
			Count(sa.name).as_("adms"),
			spt.custom_target_sfr.as_("target_sfr"),
			sa.course_purchased.as_("product")
		)
		.where((sa.date_of_sale >= filters.start_date) & (sa.date_of_sale <= filters.end_date))
		.groupby(sa.sales_person)
    )
   
    if filters.sales_person:
        main_query = main_query.where(sa.sales_person == filters.sales_person)
    if filters.product:
        main_query = main_query.where(sa.course_purchased == filters.product)

    main_query = main_query.run(as_dict=1)
    
    for row in main_query:
        target = row.get("target") or 0
        sales_collection = row.get("sales_collection") or 0
        total_sale_value = row.get("total_sale_value") or 0
        adms = row.get("adms") or 0
        sfr = row.get("sfr") or 1
        target_sfr = row.get("target_sfr") or 1

        row["target_perc"] = (round(sales_collection / target * 100, 2)) if target else 0
        row["progress"] = (round(total_sale_value / target * 100, 2)) if target else 0
        row["sfr_perc"] = (round((sfr / target_sfr) * 100, 2)) if target_sfr else 0
        row["acr"] = (round(adms / sfr, 2)) if sfr else 0
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
				(sa.date_of_sale >= filters.start_date) &
				(sa.date_of_sale <= filters.end_date) &
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
    chart = {
        "data": {
            "labels": [],
            "datasets": [
                {
                    "name": "Sales Progress (%)",
                    "values": []
                }
            ]
        },
        "type": "bar", 
        "height": 300,
        "title": "SALES CHAMPIONS"
    }
    chart_data = (
        frappe.qb.from_(sa)
        .left_join(spt).on(sa.sales_person == spt.sales_person)
        .select(spt.target, sa.sales_person, Sum(sa.total_sale_value).as_("total_sale_value"))
        .groupby(sa.sales_person)
        .run(as_dict=1)
    )
    
    
    for data_row in chart_data:
        chart['data']['labels'].append(data_row['sales_person'])
        percentage = (data_row['total_sale_value'] / data_row['target'])*100
        chart['data']['datasets'][0]['values'].append(percentage)
    return columns, data, None, chart
