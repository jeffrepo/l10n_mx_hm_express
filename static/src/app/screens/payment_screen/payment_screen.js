/** @odoo-module **/

import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { rpc } from '@web/core/network/rpc';

patch(PaymentScreen.prototype, {
    /**
     * Parcheamos validateOrder para añadir lógica antes o después de la validación estándar.
     */
    async validateOrder(isForceValidate) {
        // --- AQUÍ VA TU LÓGICA ANTES DE LA VALIDACIÓN ORIGINAL ---
        console.log("🟢 what's up man - Lógica agregada antes de validar la orden.");
        const order = this.pos.get_order();
        console.log("Que es this in validate_order ", this)
        console.log("Que es order in validate_order ", order)
        // llamamos a Python vía RPC
        const amount_total_words = await this.getAmountTotalWords(order.amount_total, order.config_id.currency_id.id);
        order.amount_total_words = amount_total_words;
        // Llamar al método validateOrder original. 
        // Es crucial usar 'await' porque el método original es async.
        const result = await super.validateOrder(isForceValidate);

        // --- AQUÍ PUEDES AGREGAR MÁS LÓGICA DESPUÉS DE LA VALIDACIÓN ORIGINAL ---
        
        return result;
    },

    async getAmountTotalWords(total, currency_id) {
        console.log("🔤 Llamando a Python para convertir monto a letras:", total);
        try {
            const result = await rpc("/web/dataset/call_kw/pos.order/get_amount_total_words", {
                model: "pos.order",
                method: "get_amount_total_words",
                args: [total, currency_id],
                kwargs: {},
            });
            console.log("✅ Resultado desde Python:", result);
            return result;
        } catch (error) {
            console.error("❌ Error al convertir monto:", error);
            return "";
        }
    },

});