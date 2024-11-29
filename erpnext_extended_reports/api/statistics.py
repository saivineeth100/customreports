
import json

import frappe
from frappe.query_builder.functions import Sum, Count
doc_child_relations = {"Account": {
    "doctype": "Account",  "group_by": "parent_account"
}}
disabled_filter = {"disabled": False}

doctypes_list = [
    {"doctype": "Account", "label": "Account",
     "filters": {"disabled": False},
     "childs":
                [
                    {"doctype": "Account", "label": "Account Groups",
                        "filters": {"is_group": True, }, },
                    {"doctype": "Account", "label": "Accounts",
                     "filters": {"is_group": False}}
     ]
     },
    # {
    #     "doctype": "Item Group", "label": "Item Group", "filters": {},
    # }, {
    #     "doctype": "Item", "label": "Item", "filters": {},
    # },
    # {
    #     "doctype": "Cost Center", "label": "Cost Center", "filters": disabled_filter,
    # },
    # {
    #     "doctype": "Bank", "label": "Bank", "filters": {},
    # },
    # {
    #     "doctype": "Bank Account", "label": "Bank Account", "filters": disabled_filter,
    # },
    # {
    #     "doctype": "Budget", "label": "Budget", "filters": {},
    # },
    # {
    #     "doctype": "Currency", "label": "Currency", "filters": {"enabled": True},
    # }
]


@frappe.whitelist(methods=["GET"])
def get_stats_master(company: str, show_disabled_count=False):

    data = []
    for doc in doctypes_list:
        filters = doc.get("filters", {})

        filters["company"] = company
        data.append(getDocData({**doc, "filters": {**filters}}))
    return {"data": data}


@frappe.whitelist(methods=["POST"])
def get_stats_trans(show_cancelled_count=False):
    is_submitted_filter = {"status": "Submitted"}
    data = []
    return {data}


@frappe.whitelist(methods=["POST"])
def get_stats_trans_monthly_grouped(doc_type: str, show_cancelled_count=False):
    is_submitted_filter = {"status": "Submitted"}
    data = []
    return {data}


def getDocData(doc: str):
    doc_data = {"name": doc["label"]}
    main_filters = doc.get("filters", {})
    doc_data["count"] = getCount(doc["doctype"], main_filters)
    doc_data["childs"] = getChildsDocData(doc.get("childs", []), main_filters)
    return doc_data


def getChildsDocData(childs, main_filters):
    child_docs = []
    if (len(childs) == 0):
        return child_docs

    for child in childs:
        doc = {**child, "filters": {**child["filters"], **main_filters}}
        child_docs.append(getDocData(doc))
    return child_docs


def getCount(doc_type: str, filters: dict[str, str | int] | None = None):
    frappe.db.count
    count_query = frappe.qb.from_(doc_type).select(Count("*"))
    for key in filters:
        count_query = count_query.where(frappe.qb.Field(key) == filters[key])
    count = count_query.run()
    return count[0][0]


def getCountGroupBy(doc, main_filters):
    if doc is None:
        return []
    group_by = doc["group_by"]
    field = frappe.qb.Field(group_by)
    count_query = frappe.qb.from_(doc["doctype"]).select(
        field.as_("name"), Count("*").as_("count")).groupby(group_by)
    filters = {**doc.get("filters", {}), **main_filters}
    for key in filters:
        count_query = count_query.where(frappe.qb.Field(key) == filters[key])
    count_query = count_query.where(field.isnotnull())
    counts = count_query.run(as_dict=1)
    # counts = str(count_query)
    return counts
