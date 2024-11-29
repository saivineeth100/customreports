frappe.provide("erpnext.stats_report");
frappe.pages['report-statistics'].on_page_load = function (wrapper) {

	frappe.stats_report = new erpnext.stats_report.Controller(wrapper)
	//this.$type = "transaction"
	$(wrapper).bind("show", () => {
		let route = frappe.get_route()[1]
		console.log(`route - ${route},type =${frappe.stats_report.$type},${route != frappe.stats_report.$type}`)
		if (frappe.stats_report.$type == undefined) {
			let type = route || "transaction";
			frappe.stats_report.$sidebar_list
				.find(`[stat-type = "${type}"]`).trigger("click");
		}
	})


}

erpnext.stats_report.Controller = class {
	constructor(wrapper) {
		frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Statistics Report',
			single_column: false,
			card_layout: true,
		});
		this.parent = wrapper;
		this.page = this.parent.page;

		this.company_field = this.page.add_field({
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
			change: function () {
				if (this.get_value()) {
					let report = frappe.stats_report
					report.load_stats(report.$type)
				}
			}
		})
		// this.page.add_field({
		// 	fieldtype: "Break",
		// })
		console.log(this.company_field)
		this.$container = $(`<div class="stats pt-4  page-main-content">	
			<div class="stats-master"></div>
			<div class="stats-trans"></div>			
		</div>`).appendTo(this.page.main)

		this.page.sidebar.html(
			`<ul class="standard-sidebar stats-sidebar overlay-sidebar">
		<li class="standard-sidebar-item" >
			<span>${frappe.utils.icon("customer", "md")}</span>
			<a class="sidebar-link" stat-type="transaction">
				<span >Transactions</span>
			</a>
		</li>
			<li class="standard-sidebar-item" >
			<span>${frappe.utils.icon("customer", "md")}</span>
			<a class="sidebar-link" stat-type="master">
				<span >Masters</span>
			</a>
		</li>
		</ul>`
		);
		this.$sidebar_list = this.page.sidebar.find(".stats-sidebar");
		this.$stats_master = this.page.main.find(".stats-master");
		this.$stats_trans = this.page.main.find(".stats-trans");

		//console.log([this.$stats_master, this.$stats_trans])
		this.$sidebar_list.on("click", "li", (e) => {

			let $li = $(e.currentTarget);
			let type = $li.find(".sidebar-link").attr("stat-type");
			if (this.$type === type) {
				return
			}
			this.$sidebar_list.find(".active").removeClass("active selected");
			$li.addClass("active selected");
			this.load_stats(type)
		})
		let btn = this.page.set_secondary_action('Refresh', () => {

			this.load_stats(this.$type)
		}, 'octicon octicon-sync')
	}
	load_stats(type) {
		this.$stats_trans.empty();
		this.$stats_master.empty();
		this.$type = type
		const company = this.company_field.get_value()
		frappe.set_route("report-statistics", this.$type);
		if (this.$type == "master") {
			this.$stats_trans.empty()
			frappe.call({ method: "erpnext_extended_reports.api.statistics.get_stats_master", args: { company }, type: "GET" })
				.then((res) => {

					$(`<div  class="list-group">
						<div  class="list-group-item ">
						 	<div class="d-flex w-100 justify-content-between">
						  	<h5 class="mb-1">Name</h5>
						   <small>Count</small>
							</div>
						</div>
						${this.getChildItems(res.message?.data)}
						</div>`).appendTo(this.$stats_master)
				})

		}
		else {
			this.$stats_master.empty()

			$(`<h1>Trans Stats</h1>`).appendTo(this.$stats_trans)
		}
	}
	getChildItems(items, ischild = false) {
		if (items == undefined) {
			return ""
		}
		return items?.map(data => {
			return `
			<li  class="list-group-item border-bottom-0  ${ischild ? "pr-0 py-1 m-0 border-0" : "pb-2"}" >
			 <div class="d-flex w-100 justify-content-between">
			  <h5 class="mb-1">${data.name}</h5>
			   <small >${data.count}</small>
			</div>
			 ${this.getNestedChildItems(data.childs)}		
			</li>`
		}).join("")
	}
	getNestedChildItems(items) {
		if (items == undefined) {
			return ""
		}
		const child_items = this.getChildItems(items, true)
		return `<ul  class="list-group ">${child_items}</ul>`
	}

}