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
        <div id="sales_chart" style="display:none;"></div>
        <div id="sales_chart_2" style="display:none;"></div>
        <div id="sales-tracker-table"></div> <!-- Sales Tracker Table -->
        <div id="sfr-tracker-table"></div> <!-- SFR Tracker Table -->
    `;

	$(wrapper).html(filters_html);

	// Load dropdowns for Academic Counselor and Product
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

	// Apply Filters event
	$('#apply_filters').on('click', function () {
		let start_date = $('#start_date').val();
		let end_date = $('#end_date').val();
		let acad_coun = $('#acad_coun_filter').val();
		let product = $('#product_filter').val();

		if (!start_date || !end_date) {
			frappe.msgprint(__('Please select both start and end dates.'));
			return;
		}

		$("#sales_chart").show();
		$("#sales_chart_2").show();

		// First Chart: Sales Champions (Pie chart)
		frappe.call({
			method: "enrollment.enrollment.page.sales_tracker.report_data.get_sales_champions",
			args: { start_date, end_date },
			callback: function (r) {
				if (r.message) {
					let labels_1 = r.message[0];  // Array of labels
					let values_1 = r.message[1];  // Array of values

					// Debugging the data
					console.log('Sales Champions Data:', labels_1, values_1);

					// Check if the data exists
					if (labels_1 && values_1) {
						// Render Pie Chart
						new frappe.Chart("#sales_chart", {
							title: "Sales Champions",
							data: {
								labels: labels_1,
								datasets: [{
									name: "Target Progress",
									values: values_1
								}]
							},
							type: 'pie',
							height: 300,
							colors: ['#5e64ff']
						});
					}
				}
			}
		});

		// Second Chart: Top Performers (Bar chart)
		frappe.call({
			method: "enrollment.enrollment.page.sales_tracker.report_data.get_sales_champions",
			args: { start_date, end_date },
			callback: function (r) {
				if (r.message) {
					let labels_2 = r.message[2];  // Array of labels
					let values_2 = r.message[3];  // Array of values

					// Debugging the data
					console.log('Top Performers Data:', labels_2, values_2);

					// Check if the data exists
					if (labels_2 && values_2) {
						// Render Bar Chart
						new frappe.Chart("#sales_chart_2", {
							title: "Top Performers",
							data: {
								labels: labels_2,
								datasets: [{
									name: "Top Performers",
									values: values_2
								}]
							},
							type: 'bar',
							height: 300,
							colors: ['#ff6363'],
							barOptions: {
								spaceRatio: 0.3,  // Space between bars
								stacked: true      // Stack bars
							},
							axisOptions: {
								xAxisMode: "tick",  // X-axis in ticks mode
								yAxisMode: "span",  // Y-axis in span mode
								xIsSeries: true     // X-axis as series
							},
							valuesOverPoints: true  // Display values over bars
						});
					}
				}
			}
		});

		// Sales Tracker Report (Table)
		frappe.call({
			method: "enrollment.enrollment.page.sales_tracker.report_data.execute",
			args: { start_date, end_date, sales_person: acad_coun, product: product },
			callback: function (r) {
				if (r.message) {
					let html = `
                        <center><h4>Sales Tracker</h4></center>
                        <table class="table table-bordered">
                            <thead>
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
                                    <th>ARPU</th>
                                    <th>ACR</th>
                                    <th>Installment</th>
                                    <th>Installment Collection</th>`;
					r.message[1].forEach(day => {
						html += `<th>${day}</th>`;
					});
					html += `</tr>
                            </thead>
                            <tbody>`;
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
                            <td>${row.arpu }</td>
                            <td>${row.acr }</td>
                            <td>${row.installment}</td>
                            <td>${row.installment_collection}</td>`;
						r.message[1].forEach(day => {
							html += `<td>${row[day]}</td>`;
						});
						html += `</tr>`;
					});
					html += `</tbody></table>`;
					$(wrapper).find("#sales-tracker-table").html(html);
				}
			}
		});

		// SFR Tracker Report (Table)
		frappe.call({
			method: "enrollment.enrollment.page.sales_tracker.report_data.sfr_tracker",
			args: { start_date, end_date, sales_person: acad_coun, product: product },
			callback: function (r) {
				if (r.message) {
					let html = `
                        <center><h4>SFR Tracker</h4></center>
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>Academic Counselor</th>
                                    <th>Progress</th>
									<th>SFR Rank</th>
                                    <th>SFR %</th>
									<th>Leave</th>
                                    <th>Target Sfr</th>
                                    <th>Actual Sfr</th>`;
					r.message[1].forEach(day => {
						html += `<th>${day}</th>`;
					});
					html += `</tr>
                            </thead>
                            <tbody>`;
					r.message[0].forEach(row => {
						html += `<tr>
                            <td>${row.sales_person}</td>
                            <td>${row.progress}</td>
							<td>${row.rank} </td>
                            <td>${row.sfr_perc}</td>
							<td>${row.leave}</td>
                            <td>${row.target_sfr}</td>
                            <td>${row.sfr}</td>`;
						r.message[1].forEach(day => {
							html += `<td>${row[day]}</td>`;
						});
						html += `</tr>`;
					});
					html += `</tbody></table>`;
					$(wrapper).find("#sfr-tracker-table").html(html);
				}
			}
		});

	});
};
