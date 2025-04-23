# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt

import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum, Count

def execute(filters=None):
	data = []
	columns = [
        {"label": "Target Crusher", "fieldname": "tc", "fieldtype": "Data", "width": 120},
        {"label": "Coversion Pro", "fieldname": "con_pro", "fieldtype": "Data", "width": 120},
        {"label": "Admission Star", "fieldname": "adm_star", "fieldtype": "Data", "width": 120} 
    ]
	sa = DocType("Sales Activity")
	spt= DocType("Sales Person Target")
	chart = {
        "data": {
            "labels": [],
            "datasets": [{"name": "top performers", "values": []}]
        },
        "type": "bar"
    }
    
	top_perf = (
		frappe.qb.from_(sa)
		.left_join(spt).on(sa.sales_person == spt.sales_person)
		.select(spt.target, sa.sales_person, Sum(sa.total_sale_value).as_("tot_sal_val"), Count(sa.name).as_("admission"), Sum(sa.connected_calls).as_("sfr"))
		.groupby(sa.sales_person)
		.run(as_dict=1)
	)
	
	for perf_det in top_perf:
		perf_det['conversion'] = perf_det["admission"] / perf_det["sfr"] if perf_det["sfr"] !=0 else 0
	
	target_crusher_detail = max(top_perf, key=lambda x: x["tot_sal_val"])
	coversion_pro_detail = max(top_perf, key=lambda x: x["conversion"])
	admission_star = max(top_perf, key=lambda x: x["admission"])
	
	data.append({"tc": target_crusher_detail['sales_person'] + "(Target Crusher)", "con_pro": coversion_pro_detail['sales_person'] + "(Coversion Pro)", "adm_star": admission_star['sales_person']+ "(Admission Star)"})
	chart['data']['labels'].append(data[0]['tc'])
	chart['data']['labels'].append(data[0]['con_pro'])
	chart['data']['labels'].append(data[0]['adm_star'])
	
	tcp = (target_crusher_detail['tot_sal_val'] / target_crusher_detail["target"] ) * 100
	chart['data']['datasets'][0]['values'].append(tcp)
	chart['data']['datasets'][0]['values'].append(coversion_pro_detail['conversion'])
	chart['data']['datasets'][0]['values'].append(admission_star['admission']) 
	return columns, data, None, chart
