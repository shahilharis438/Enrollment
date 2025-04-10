# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt

import frappe
from collections import defaultdict

def execute(filters=None):
    filters = filters or {}
    from_date = filters.get("date_from")
    to_date = filters.get("date_to")

    columns = [
        {"label": "Course", "fieldname": "course", "fieldtype": "Data", "width": 200},
        {"label": "Student Name", "fieldname": "student_name", "fieldtype": "Data", "width": 180},
        {"label": "Enrollment Date", "fieldname": "enrollment_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 100},
        {"label": "Email", "fieldname": "email", "fieldtype": "Data", "width": 200},
        {"label": "Status Count", "fieldname": "status_count", "fieldtype": "Data", "width": 200}
    ]

    conditions = []
    if from_date:
        conditions.append("enrollment_date >= %(date_from)s")
    if to_date:
        conditions.append("enrollment_date <= %(date_to)s")

    where_clause = " AND ".join(conditions)
    if where_clause:
        where_clause = "WHERE " + where_clause

    query = f"""
        SELECT
            student_name,
            course,
            enrollment_date,
            status,
            email
        FROM `tabStudent Enrollment Details`
        {where_clause}
        ORDER BY course, enrollment_date DESC
    """

    data = frappe.db.sql(query, filters, as_dict=True)

    grouped_data = defaultdict(list)
    status_summary = defaultdict(lambda: defaultdict(int))

    for row in data:
        grouped_data[row.course].append(row)
        status_summary[row.course][row.status] += 1

    final_data = []
    for course, entries in grouped_data.items():
        
        status_str = ", ".join(f"{k}: {v}" for k, v in status_summary[course].items())
        final_data.append({
            "course": course,
            "status_count": status_str
        })
        for row in entries:
            final_data.append({
                "course": "->",
                "student_name": row.student_name,
                "enrollment_date": row.enrollment_date,
                "status": row.status,
                "email": row.email
            })

    return columns, final_data    