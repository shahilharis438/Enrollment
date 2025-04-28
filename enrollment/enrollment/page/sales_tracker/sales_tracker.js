frappe.pages['sales-tracker'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Tracker',
		single_column: true
	});

	// Filters HTML
	var filters_html = `
		<div class="filters">
			<label>Start Date</label>
			<input type="date" id="start_date">
			
			<label>End Date</label>
			<input type="date" id="end_date">
			
			<label>Academic Counselor</label>
			<select id="acad_coun_filter">
				<option value="">Select Counselor</option>
			</select>
			
			<label>Product</label>
			<select id="product_filter">
				<option value="">Select Product</option>
			</select>
			
			<button id="apply_filters">Apply Filters</button>
		</div>
		<div id="sales_chart" style="display:none;"></div> <!-- Initially hide the chart -->
		<div id="report-table"></div>
	`;

	$(wrapper).html(filters_html);

	// Load dropdowns
	frappe.call({
		method: "frappe.client.get_list",
		args: {
			doctype: "Sales Person",
			fields: ["sales_person_name"]
		},
		callback: function (r) {
			let acad_coun_filter = $('#acad_coun_filter');
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
			let product_filter = $('#product_filter');
			r.message.forEach(function (product) {
				product_filter.append(`<option value="${product.name}">${product.name}</option>`);
			});
		}
	});

	// On click Apply Filters
	$('#apply_filters').on('click', function () {
		let start_date = $('#start_date').val();
		let end_date = $('#end_date').val();
		let acad_coun = $('#acad_coun_filter').val();
		let product = $('#product_filter').val();

		// Show the chart container
		$("#sales_chart").show();

		// Get Chart Data
		frappe.call({
			method: "enrollment.enrollment.page.sales_tracker.report_data.get_sales_champions",
			args: {
				start_date: start_date,
				end_date: end_date,
				sales_person: acad_coun,
				product: product
			},
			callback: function (r) {
				
				console.log("Chart data response:", r.message);

				if (r.message ) {
					let labels = r.message[0];
					let values = r.message[1];

					// r.message.forEach(item => {
					// 	labels.push(item.name || "Unknown");
					// 	values.push(item.sfr_percent || 0);
					// });

					
					// if ($("#sales_chart").length > 0) {
						// Create the chart
						new frappe.Chart("#sales_chart", {
							title: "SFR % by Academic Counselor",
							data: {
								labels: labels,
								datasets: [
									{
										name: "SFR %",
										values: values
									}
								]
							},
							type: 'bar',
							height: 300,
							colors: ['#5e64ff']
						});
					// }
				} 
				// else {
				// 	$("#sales_chart").html("<p>No data available for the selected filters.</p>");
				// }
			}
		});

		// Get Report Data
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
							<th>SFR %</th>
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
							<th>Installment Collection</th>`;

					for (let i = 0; i < r.message[1].length; i++) {
						let day = r.message[1][i];
						html += `<th>${day}</th>`;
					}

					html += `</tr>`;

					r.message[0].forEach(row => {
						html += `<tr>
							<td>${row.acad_coun}</td>
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
							<td>${row.installment_collection}</td>`;

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
