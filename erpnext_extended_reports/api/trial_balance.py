

import json

import frappe
from frappe.query_builder.functions import Sum, Count


@frappe.whitelist(methods=["GET"])
def get_trial_balance(company: str, groups_visible: bool = False):

    return {"data": []}
