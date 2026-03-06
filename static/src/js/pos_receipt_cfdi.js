/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    export_for_printing(baseUrl, headerData) {
        console.log("mx_cfdi")
        console.log(this.mx_cfdi)
        return {
            ...super.export_for_printing(...arguments),
            mx_cfdi: this.mx_cfdi || null,
        };
    },
});


