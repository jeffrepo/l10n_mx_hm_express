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
        
        const result = await super.validateOrder(isForceValidate);

        await this.sendingLinesCreate(order);
        
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

    async sendingLinesCreate(order) {
        console.log("📦 Preparando datos del pedido:", order);
        
        try {
            // Obtener las líneas correctamente - usa order.lines en lugar de order.orderlines
            const orderLines = order.lines || order.get_orderlines?.() || [];
            
            console.log("📋 Líneas del pedido:", orderLines);
            
            const lineData = orderLines.map(line => ({
                product_id: line.product_id?.id || false,
                product_name: line.product_id?.name || '',
                product_default_code: line.product_id?.default_code || '',
                qty: line.qty || 0,
                price_unit: line.price_unit || 0,
                price_subtotal: line.price_unit * line.qty || 0,
                discount: line.discount || 0,
                line_note: line.note || '',
                order_id: line.order_id?.id || false,
                state: line.order_id?.state || false,
            }));

            console.log("📤 Enviando datos procesados:", lineData);

            const result = await rpc("/web/dataset/call_kw/pos.remission/new_lines_create", {
                model: "pos.remission",
                method: "new_lines_create",
                args: [lineData],
                kwargs: {},
            });
            
            console.log("✅ Líneas creadas exitosamente:", result);
            return result;
        } catch (error) {
            console.error("❌ Error al crear las líneas:", error);
            return {'success': false, 'error': error.message};
        }
    }

});