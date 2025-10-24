import { PosOrder } from "@point_of_sale/app/models/pos_order"; 
import { patch } from "@web/core/utils/patch"; 
patch(PosOrder.prototype, { 
    export_for_printing(baseUrl, headerData) {
         console.log("Ahora si creo que estamos heredando ", this); 
          
         return { 
            ...super.export_for_printing(...arguments), 
            delivery_note_custom: this.delivery_note_custom, 
            partner_id: this.partner_id, 
            orderlines_custom: this.lines, 
            amount_total_words: this.amount_total_words
        }; 
    }, 
     
});