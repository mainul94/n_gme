import frappe


def clear_cache(doc=None, method=None):
    for key in frappe.cache().hgetall('contacts'):
        frappe.cache().hdel('contacts', key)
