# Copyright (c) 2025, shahil and Contributors
# See license.txt

# import frappe
from frappe.tests.utils import FrappeTestCase


import frappe
from frappe.tests.utils import FrappeTestCase
from frappe import _

class TestStudentEnrollmentDetails(FrappeTestCase):

    def setUp(self):
        frappe.db.delete("Student Enrollment Details", {"student_name": "Test Student"})

    def create_doc(self, **kwargs):
        defaults = {
            "doctype": "Student Enrollment Details",
            "student_name": "Test Student",
            "course": "Python 101",
            "email": "test@student.com",
            "status": "Pending"
        }
        defaults.update(kwargs)
        return frappe.get_doc(defaults)

    def test_missing_fields(self):
        doc = self.create_doc(student_name=None, course=None, email=None)
        with self.assertRaises(frappe.ValidationError) as e:
            doc.validate()
        self.assertIn("Missing required field(s): Student Name, Course, Email", str(e.exception))

    def test_invalid_email(self):
        doc = self.create_doc(email="invalid-email")
        with self.assertRaises(frappe.ValidationError) as e:
            doc.validate()
        self.assertIn("Please enter a valid email address.", str(e.exception))

    def test_empty_course_field(self):
        doc = self.create_doc(course="   ")
        with self.assertRaises(frappe.ValidationError) as e:
            doc.validate()
        self.assertIn("Course field cannot be empty or just spaces.", str(e.exception))

    def test_duplicate_enrollment(self):
       
        existing_doc = self.create_doc()
        existing_doc.insert()

        
        new_doc = self.create_doc()
        new_doc.name = "Another Name"  
        with self.assertRaises(frappe.ValidationError) as e:
            new_doc.validate()
        self.assertIn("This student is already enrolled in this course.", str(e.exception))

    def test_send_approval_notification_flag(self):
        doc = self.create_doc(status="Approved")
        doc.flags.notified_approved = False

       
        frappe.sendmail = lambda *args, **kwargs: None

        doc.on_update()
        self.assertTrue(doc.flags.notified_approved)

    def test_send_approval_notification_content(self):
        doc = self.create_doc(
            student_name="Jane Doe",
            course="Data Science",
            status="Approved",
            enrollment_date="2024-01-01"
        )

       
        sent = {}

        def fake_sendmail(**kwargs):
            sent.update(kwargs)

        frappe.sendmail = fake_sendmail
        doc.send_approval_notification()

        self.assertIn("Jane Doe", sent["subject"])
        self.assertIn("Data Science", sent["message"])
        self.assertIn("2024-01-01", sent["message"])
