frappe.pages['sales-tracker'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Tracker',
		single_column: true
	});

	
	var filters_html = `
        <div class="filters">
            <label>Start Date</label>
            <input type="date" id="start_date">
            
            <label>End Date</label>
            <input type="date" id="end_date">
            
            <label>Academic Counselor</label>
            <select id="acad_coun_filter">
                <option value="">Select Counselor</option>
                <!-- Options will be loaded dynamically -->
            </select>
            
            <label>Product</label>
            <select id="product_filter">
                <option value="">Select Product</option>
                <!-- Options will be loaded dynamically -->
            </select>
            
            <button id="apply_filters">Apply Filters</button>
        </div>
    `;

	$(wrapper).html(filters_html + '<div id="report-table"></div>');

	
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Sales Person",
			fields: ["sales_person_name"]
		},
		callback: function (r) {
			var acad_coun_filter = $('#acad_coun_filter');
			r.message.forEach(function (sales_person) {
				acad_coun_filter.append(`<option value="${sales_person.sales_person_name}">${sales_person.sales_person_name}</option>`);
			});
		}
	});

	
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Product",
			fields: ["name"]
		},
		callback: function (r) {
			var product_filter = $('#product_filter');
			r.message.forEach(function (product) {
				product_filter.append(`<option value="${product.name}">${product.name}</option>`);
			});
		}
	});

	
	$('#apply_filters').on('click', function () {
		var start_date = $('#start_date').val();
		var end_date = $('#end_date').val();
		var acad_coun = $('#acad_coun_filter').val();
		var product = $('#product_filter').val();

		frappe.call({
			method: "enrollment.enrollment.page.sales_tracker.report_data.execute",
			args: {
				start_date: start_date,
				end_date: end_date,
				sales_person: acad_coun,
				product: product
			},
			callback: function (r) {
				if (r.message) {
					let html = `<table class="table table-bordered">
                    <tr>
                    <th>Academic Counselor</th>
                    <th>Progress</th>
					<th>SFR</th>
					<th">SFR %</th>
					<th>Target Sfr</th>
					<th>Adms</th>
					<th>Sale Value</th>
					<th>Sale Collection</th>
					<th>Target</th>
					<th>Target %</th>
					<th>Outstanding</th>
					<th>Arpu</th>
					<th>Acr</th>
					<th>Installment</th>
					<th>Installment Collection</th>
					`;
					
					
					for (let i = 0; i < r.message[1].length ; i++) {
						let day = r.message[1][i];
						html += `<th>${day}</th>`;
					}

					html += `</tr>`;

					
					r.message[0].forEach(row => {
						html += `<tr>
                    <td >${row.acad_coun}</td>
                    <td>${row.progress}</td>
					<td>${row.sfr}</td>
					<td>${row.sfr_perc}</td>
					<td>${row.target_sfr}</td>
					<td>${row.adms}</td>
					<td>${row.total_sale_value}</td>
					<td>${row.sales_collection}</td>
					<td>${row.target}</td>
					<td>${row.target_perc}</td>
					<td>${row.outstanding}</td>
					<td>${row.arpu}</td>
					<td>${row.acr}</td>
					<td>${row.installment}</td>
					<td>${row.installment_collection}</td>
					`;
					
					r.message[1].forEach(day => {
							html += `<td>${row[day]}</td>`;
					});
						

						html += `</tr>`;
					});

					html += `</table>`;

					$(wrapper).find("#report-table").html(html);
				}

			}
		});
	});
};
