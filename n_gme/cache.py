import frappe
from frappe.email import get_cached_contacts, build_match_conditions, update_contact_cache

def clear_cache(doc=None, method=None):
    for key in frappe.cache().hgetall('contacts'):
        frappe.cache().hdel('contacts', key)



@frappe.whitelist()
def get_contact_list(txt, page_length=20):
    """Returns contacts (from autosuggest)"""

    # cached_contacts = get_cached_contacts(txt)
    # if cached_contacts:
    # 	return cached_contacts[:page_length]

    match_conditions = build_match_conditions("Contact")
    match_conditions = "and {0}".format(match_conditions) if match_conditions else ""

    out = frappe.db.sql(
        """select email_id as value,
        concat(first_name, ifnull(concat(' ',last_name), '' )) as description
        from tabContact
        where coalesce(email_id, '')!='' and name like %(txt)s or email_id like %(txt)s
        %(condition)s
        limit %(page_length)s""",
        {"txt": "%" + txt + "%", "condition": match_conditions, "page_length": page_length},
        as_dict=True,
    )
    out = filter(None, out)

    # update_contact_cache(out)
    return out
