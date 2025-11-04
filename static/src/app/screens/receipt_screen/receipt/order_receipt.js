/** @odoo-module **/

import { OrderReceipt } from "@point_of_sale/app/screens/receipt_screen/receipt/order_receipt";
import { patch } from "@web/core/utils/patch";

// Aplicamos un parche al componente OrderReceipt original
patch(OrderReceipt.prototype, {
    /**
     * @override
     */
    getNewData() {
        console.log("This props data ", this.props.data, "\n\n\n")
        console.log("this props ",  this.props, "\n\n\n")
        console.log(this)
        const partner = this.props.data.partner_id;
        this.props.data.headerData.delivery_note_custom = this.props.data.delivery_note_custom
        this.props.data.headerData.date = this.props.data.date
        this.props.data.headerData.pos_reference = this.props.data.name
        // Usamos optional chaining para acceder a 'name' solo si 'partner' existe.
        return true;
    },
});


