import frappe
import json
from frappe.desk.form.load import (_get_communications, get_attachments, get_comments, get_versions, get_assignments, get_doc_permissions,
                                   get_view_logs, get_point_logs, get_additional_timeline_content, get_milestones, is_document_followed, get_tags, get_document_email, run_onload)


@frappe.whitelist()
def getdoc(doctype, name, user=None):
    """
    Loads a doclist for a given document. This method is called directly from the client.
    Requries "doctype", "name" as form variables.
    Will also call the "onload" method on the document.
    """

    if not (doctype and name):
        raise Exception("doctype and name required!")

    if not name:
        name = doctype

    if not frappe.db.exists(doctype, name):
        return []

    try:
        doc = frappe.get_doc(doctype, name)
        run_onload(doc)

        if not doc.has_permission("read"):
            frappe.flags.error_message = _("Insufficient Permission for {0}").format(
                frappe.bold(doctype + " " + name)
            )
            raise frappe.PermissionError(("read", doctype, name))

        doc.apply_fieldlevel_read_permissions()

        # add file list
        doc.add_viewed()
        get_docinfo(doc)

    except Exception:
        raise

    doc.add_seen()

    frappe.response.docs.append(doc)


@frappe.whitelist()
def get_docinfo(doc=None, doctype=None, name=None):
    if not doc:
        doc = frappe.get_doc(doctype, name)
        if not doc.has_permission("read"):
            raise frappe.PermissionError

    all_communications = _get_communications(
        doc.doctype, doc.name, limit=100000)
    automated_messages = [
        msg for msg in all_communications if msg["communication_type"] == "Automated Message"
    ]
    communications_except_auto_messages = [
        msg for msg in all_communications if msg["communication_type"] != "Automated Message"
    ]

    frappe.response["docinfo"] = {
        "attachments": get_attachments(doc.doctype, doc.name),
        "attachment_logs": get_comments(doc.doctype, doc.name, "attachment"),
        "communications": communications_except_auto_messages,
        "automated_messages": automated_messages,
        "comments": get_comments(doc.doctype, doc.name),
        "total_comments": len(json.loads(doc.get("_comments") or "[]")),
        "versions": get_versions(doc),
        "assignments": get_assignments(doc.doctype, doc.name),
        "assignment_logs": get_comments(doc.doctype, doc.name, "assignment"),
        "permissions": get_doc_permissions(doc),
        "shared": frappe.share.get_users(doc.doctype, doc.name),
        "info_logs": get_comments(doc.doctype, doc.name, comment_type=["Info", "Edit", "Label"]),
        "share_logs": get_comments(doc.doctype, doc.name, "share"),
        "like_logs": get_comments(doc.doctype, doc.name, "Like"),
        "workflow_logs": get_comments(doc.doctype, doc.name, comment_type="Workflow"),
        "views": get_view_logs(doc.doctype, doc.name),
        "energy_point_logs": get_point_logs(doc.doctype, doc.name),
        "additional_timeline_content": get_additional_timeline_content(doc.doctype, doc.name),
        "milestones": get_milestones(doc.doctype, doc.name),
        "is_document_followed": is_document_followed(doc.doctype, doc.name, frappe.session.user),
        "tags": get_tags(doc.doctype, doc.name),
        "document_email": get_document_email(doc.doctype, doc.name),
    }
