
import json

import frappe
from frappe.query_builder.functions import Sum, Count


@frappe.whitelist(methods=["GET"])
def get_stats_master(show_disabled_count=False):
    disabled_filter = {"disabled": True}
    doctypes_list = [
        {"doctype": "Account", "label": "Account",
            "filters": {"disabled": False},
            "childs":
                [
                    {"doctype": "Account", "label": "Account Groups",
                        "filters": {"is_group": True, }, "childs_group_by": {
                            "doctype": "Account", "group_by": "parent_account"
                        }},
                    {"doctype": "Account", "label": "Accounts",
                     "filters": {"is_group": False}}
            ]
         },
    ]
    data = []
    for doc in doctypes_list:        
        data.append(getDocData(doc))
    return {"data": data}


def getDocData(doc):
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
    count_query = frappe.qb.from_(doc_type).select(Count("*"))
    for key in filters:
        count_query = count_query.where(frappe.qb.Field(key) == filters[key])
    count = count_query.run()
    return count


def getCountGroupBy(doc_type: str, group_by: str, filters: dict[str, str | int] | None = None):
    count_query = frappe.qb.from_(doc_type).select(
        Count("*"))
    frappe.get_all
    for key in filters:
        count_query.where(frappe.qb.Field(key) == filters[key])
    count = count_query.run()


@frappe.whitelist(methods=["POST"])
def get_stats_trans(show_cancelled_count=False):
    is_submitted_filter = {"status": "Submitted"}
    data = []
    return {data}
