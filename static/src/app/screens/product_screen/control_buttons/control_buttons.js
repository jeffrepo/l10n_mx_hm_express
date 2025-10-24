/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

// 1. Importar el componente del botón.
// (Asegúrate de que esta ruta sea correcta con respecto a este archivo JS)
import { NotaRemisionButton } from "./nota_remision_button"; 

// --- PARCHEO DE LA CLASE ESTATICA (Añadir Componente) ---
// Ahora solo pasamos DOS argumentos: el objeto a parchear (ControlButtons) y el objeto con las propiedades.
patch(ControlButtons, {
    // 2. Registra el nuevo componente como subcomponente de ControlButtons.
    // Esto lo hace disponible en la plantilla XML de ControlButtons.
    components: {
        ...ControlButtons.components,
        NotaRemisionButton,
    },
});

// --- PARCHEO DEL PROTOTIPO (Añadir Lógica) ---
// También corregimos el parche del prototipo para usar solo DOS argumentos.
patch(ControlButtons.prototype, {
    setup() {
        super.setup();
        console.log("🟢 ControlButtons parcheado correctamente");
    },
});
