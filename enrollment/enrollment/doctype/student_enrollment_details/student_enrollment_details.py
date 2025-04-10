# Copyright (c) 2025, shahil and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate

class StudentEnrollmentDetails(Document):
    def before_submit(self):
      if self.workflow_state:
        self.status = self.workflow_state
    
    def validate(self):
        
        missing_fields = []

        if not self.student_name:
            missing_fields.append("Student Name")
        if not self.course:
            missing_fields.append("Course")
        if not self.email:
            missing_fields.append("Email")

        if missing_fields:
            frappe.throw(f"Missing required field(s): {', '.join(missing_fields)}")

        
        if "@" not in self.email or "." not in self.email:
            frappe.throw("Please enter a valid email address.")

        
        

        if self.course and not self.course.strip():
            frappe.throw("Course field cannot be empty or just spaces.")

        
        if frappe.db.exists(
            "Student Enrollment Details",
            {
                "student_name": self.student_name,
                "course": self.course,
                "email": self.email,
                "docstatus": ["!=", 2],  
                "name": ["!=", self.name] 
            }
        ):
            frappe.throw("This student is already enrolled in this course.")
    def on_update(self):
        if self.status == "Approved" and not self.flags.notified_approved:
            self.send_approval_notification()
            self.flags.notified_approved = True  

    def send_approval_notification(self):
        recipient = "shahilharis78@gmail.com"
        subject = f"Enrollment Approved for {self.student_name}"
        message = f"""
            <p>Hello,</p>
            <p>The enrollment for <strong>{self.student_name}</strong> into the course <strong>{self.course}</strong> 
            has been <strong>approved</strong>.</p>
            <p>Enrollment Date: {self.enrollment_date}</p>
            <p>Status: {self.status}</p>
        """

        frappe.sendmail(
            recipients=[recipient],
            subject=subject,
            message=message
        )


