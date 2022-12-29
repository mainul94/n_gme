import NewWidget from "../../../../../frappe/frappe/public/js/frappe/widgets/new_widget";
import get_dialog_constructor from "../../../../../frappe/frappe/public/js/frappe/widgets/widget_dialog"
import ShortcutWidget from "../../../../../frappe/frappe/public/js/frappe/widgets/shortcut_widget";


class ShortcutWidgetExtended extends ShortcutWidget {
    edit(){
		const dialog_class = get_dialog_constructor_extend(this.widget_type);

		this.edit_dialog = new dialog_class({
			label: this.label,
			type: this.widget_type,
			values: this.get_config(),
			primary_action: (data) => {
				Object.assign(this, data);
				data.name = this.name;

				this.refresh();
			},
			primary_action_label: __("Save")
		});

		this.edit_dialog.make();
    }
    setup_events() {
		this.widget.click(() => {
			if (this.in_customize_mode) return;

            let filters = this.get_doctype_filter();
			if (this.type == "DocType" && filters) {
				frappe.route_options = filters;
			}
            let route;
            if (this.type=="DocType" && this.doc_view=="Inbox"){
                let doctype_slug = frappe.router.slug(this.link_to);
                route = `/app/${doctype_slug}/view/inbox`
            }else {
                route = frappe.utils.generate_route({
                    route: this.route,
                    name: this.link_to,
                    type: this.type,
                    is_query_report: this.is_query_report,
                    doctype: this.ref_doctype,
                    doc_view: this.doc_view
                });
            }

			
			frappe.set_route(route);
		});
	}
}

frappe.widget.widget_factory['shortcut'] = ShortcutWidgetExtended


function get_dialog_constructor_extend(type) {
    let dialog_class = get_dialog_constructor(type)
    if (type == "shortcut") {
        dialog_class =  class  ShortcutDialogExtend extends dialog_class {
            get_fields() {
                let fields = super.get_fields()
                fields.forEach(field=>{
                    if (field.fieldname=="link_to") {
                        field.onchange = () => {
                            if (this.dialog.get_value("type") == "DocType") {
                                let doctype = this.dialog.get_value("link_to");
                                if (doctype && frappe.boot.single_types.includes(doctype)) {
                                    this.hide_filters();
                                } else if (doctype) {
                                    this.setup_filter(doctype);
                                    this.show_filters();
                                }
        
                                const views = ["List", "Report Builder", "Dashboard", "Inbox", "New"];
                                if (frappe.boot.treeviews.includes(doctype)) views.push("Tree");
                                if (frappe.boot.calendars.includes(doctype)) views.push("Calendar");
        
                                this.dialog.set_df_property("doc_view", "options", views.join("\n"));
        
                            } else {
                                this.hide_filters();
                            }
                        }
                    }
                })
                return fields
            }
        }
    }
    return dialog_class
}

class NewWidgetEntend extends NewWidget {
    open_dialog() {
        const dialog_class = get_dialog_constructor_extend(this.type);

        this.dialog = new dialog_class({
            label: this.label,
            type: this.type,
            values: false,
            default_values: this.default_values,
            primary_action: this.on_create,
        });

        this.dialog.make();
    }


}

frappe.widget.WidgetGroup = class WidgetGroupExtend extends frappe.widget.WidgetGroup {
    setup_new_widget() {
        const max = this.options
            ? this.options.max_widget_count || Number.POSITIVE_INFINITY
            : Number.POSITIVE_INFINITY;

        if (this.widgets_list.length < max) {
            this.new_widget = new NewWidgetEntend({
                container: this.body,
                type: this.type,
                custom_dialog: this.custom_dialog,
                default_values: this.default_values,
                on_create: (config) => {
                    // Remove new widget
                    this.new_widget.delete();
                    delete this.new_widget;

                    config.in_customize_mode = 1;

                    // Add new widget and customize it
                    let wid = this.add_widget(config);
                    wid.customize(this.options);

                    // Put back the new widget if required
                    if (this.widgets_list.length < max) {
                        this.setup_new_widget();
                    }
                },
            });
        }
    }
}