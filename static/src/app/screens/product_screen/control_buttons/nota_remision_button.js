/** @odoo-module **/

import { Component, useState, xml } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class NotaRemisionButton extends Component {
    static props = {};
    static template = xml/* xml */`
        <button 
            class="btn btn-lg lh-lg" 
            t-att-class="state.isActive ? 'btn-success' : 'btn-light'"
            t-on-click="onClickNotaRemision"
        >
            <t t-if="state.isActive">✓ Nota remisión</t>
            <t t-else="">Nota remisión</t>
        </button>
    `;

    setup() {
        this.pos = usePos();
        this.state = useState({ 
            isActive: false  // Estado inicial
        });
    }

    onClickNotaRemision() {
        const order = this.pos.get_order();
        if (order) {
            // Alternar el estado
            this.state.isActive = !this.state.isActive;
            order.delivery_note_custom = this.state.isActive;
            
            console.log("Nota remisión:", this.state.isActive ? "Activada" : "Desactivada");
            console.log("Order:", order);
        }
    }
}