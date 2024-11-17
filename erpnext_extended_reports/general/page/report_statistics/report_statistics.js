frappe.pages['report-statistics'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Statistics R',
		single_column: true
	});
}