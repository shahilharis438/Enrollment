// Copyright (c) 2025, shahil and contributors
// For license information, please see license.txt

frappe.ui.form.on("Sales Activity", {
    lead: function (frm) {
        if (frm.doc.lead) {
            frappe.db.get_doc('Lead', frm.doc.lead)
                .then(doc => {
                    frm.set_value('lead_name', (doc.first_name || '') + ' ' + (doc.second_name || ''));
                    frm.set_value('sales_person', doc.sales_person || '');
                    frm.set_value('email', doc.email_id || '');
                    frm.set_value('mobile', doc.mobile_no || '');
                    frm.set_value('source', doc.source || '');
                })
                .catch(err => {
                    console.error('Failed to fetch Lead', err);
                });
        }
    },
    
    discount_percentage: function (frm) {
        if (frm.doc.total_sale_value && frm.doc.discount_percentage) {
            let discount = (frm.doc.discount_percentage / 100) * frm.doc.total_sale_value;
            frm.set_value("discount_amount", frm.doc.total_sale_value - discount);
        }
    },
    
    amount_paid: function (frm) {
        if (frm.doc.discount_amount && frm.doc.amount_paid) {
            frm.set_value("outstanding_amount", frm.doc.discount_amount - frm.doc.amount_paid);
        }
    },
    program_purchased: function (frm) {
        if (frm.doc.program_purchased) {
            frappe.db.get_value("Fee Structure", { "program": frm.doc.program_purchased }, "total_amount")
                .then(r => {
                    if (r && r.message && r.message.total_amount) {
                        frm.set_value("total_sale_value", r.message.total_amount);
                    }
                    else{
                        frm.set_value("total_sale_value", 0)
                    }
                });
        }
    }

});

