frappe.pages['report-trial-balance'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Trial Balance',
		single_column: true,
		card_layout: true,
	});
}