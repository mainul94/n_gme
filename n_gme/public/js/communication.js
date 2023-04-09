frappe.ui.form.on('Communication', {
    refresh: function (frm) {
        if (frm.doc.communication_type == "Communication"
            && frm.doc.communication_medium == "Email"
            && frm.doc.sent_or_received == "Received") {
            frm.custom_buttons['Forward'].unbind('click').on('click', ()=>{
                frm.trigger('forward_the_mail')
            })
        }
    },
    forward_the_mail: function (frm) {
        var args = frm.events.get_mail_args(frm)
        $.extend(args, {
            forward: true,
            subject: __("Fw: {0}", [frm.doc.subject]),
            message: frm.doc.content,
        })

        new frappe.views.CommunicationComposer(args);
    }
})
