# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, add_days, formatdate
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count


def execute(filters=None):
    data = []
    columns = [
        {"label": "Academic Counselor", "fieldname": "acad_coun", "fieldtype": "Link", "options": "Sales Person", "width": 200},
        {"label": "Progress", "fieldname": "progress", "fieldtype": "Data", "width": 180},
        {"label": "SFR", "fieldname": "sfr", "fieldtype": "Data", "width": 120},
        {"label": "ADMS", "fieldname": "adms", "fieldtype": "Data", "width": 100},
        {"label": "Sales Amount", "fieldname": "total_sale_value", "fieldtype": "Currency", "width": 200},
        {"label": "Sales Collection", "fieldname": "sales_collection", "fieldtype": "Currency", "width": 200},
        {"label": "Target", "fieldname": "target", "fieldtype": "Currency", "width": 200},
        {"label": "Outstanding", "fieldname": "outstanding", "fieldtype": "Currency", "width": 200},
        {"label": "Target Percentage", "fieldname": "target_perc", "fieldtype": "Data", "width": 200},
        {"label": "ARPU", "fieldname": "arpu", "fieldtype": "Data", "width": 200},
        {"label": "SFR Percentage", "fieldname": "sfr_perc", "fieldtype": "Data", "width": 200},
        {"label": "ACR", "fieldname": "acr", "fieldtype": "Data", "width": 200},
        {"label": "Installment", "fieldname": "installment", "fieldtype": "Data", "width": 200},
        {"label": "Installment Collection", "fieldname": "installement_collection", "fieldtype": "Currency", "width": 200},
        {"label": "Revenue", "fieldname": "revenue", "fieldtype": "Currency", "width": 200},
    ]

    if filters and filters.get("start_date") and filters.get("end_date"):
        start_date = getdate(filters.get("start_date"))
        end_date = getdate(filters.get("end_date"))

        current_date = start_date
        while current_date <= end_date:
            label = current_date.strftime("%B %-d") 
            fieldname = f"day_{current_date.strftime('%Y_%m_%d')}" 

            columns.append({
                "label": label,
                "fieldname": fieldname,
                "fieldtype": "Data",  
                "width": 120
            })

            current_date = add_days(current_date, 1)
    
    sa = DocType("Sales Activity")
    sp = DocType("Sales Person")
    spt = DocType("Sales Person Target")
    query = (
            frappe.qb
            .from_(sa)
            .join(sp)
            .on(sa.sales_person == sp.sales_person_name)
            .join(spt)
            .on(spt.sales_person ==  sa.sales_person)
            .select(
            sa.sales_person.as_("acad_coun"),
            Sum(sa.total_sale_value).as_("total_sale_value"),
            Sum(sa.amount_paid).as_("sales_collection"),
            Sum((sa.amount_paid) / spt.target * 100).as_("target_perc"),
            Sum((sa.total_sale_value) / spt.target * 100).as_("progress"),
            spt.target,
            sa.outstanding_amount.as_("outstanding"),
            Sum(sa.connected_calls).as_("sfr"),
            Count(sa.name).as_("adms"),
            Sum((sa.connected_calls) / spt.custom_target_sfr * 100).as_("sfr_perc")
            
          )
          .groupby(sa.sales_person)
          .run(as_dict=1)
    )
   
    for row in query:
        data.append(row)
    return columns, data
