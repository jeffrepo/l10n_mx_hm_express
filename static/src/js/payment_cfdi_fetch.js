/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    async _finalizeValidation() {
        await super._finalizeValidation(...arguments);
        console.log("PaymentScreen supeer");
        console.log(this);
        // 2) ya con la orden sincronizada, pide los datos CFDI
        try {
            const order = this.currentOrder;
            console.log(order)
            const uuid = order.uuid; // este es el que ves en logs del pos.order
            console.log(uuid)
            const data = await this.env.services.orm.call(
                "pos.order",
                "get_mx_cfdi_ticket_data_by_uuid",
                [uuid]
            );
            console.log("data");
            console.log(data);
            order.mx_cfdi = data || null;
        } catch (e) {
            // No rompas el flujo si falla obtener datos
            // (el ticket se imprimirá sin los extras)
        }

    },
});
