/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { onMounted, onWillUnmount } from "@odoo/owl";

patch(ProductScreen.prototype, {
    // ==================================================
    // 🔹 SETUP: se ejecuta cuando se abre la pantalla POS
    // ==================================================
    setup() {
        super.setup?.();

        // Función que escucha el teclado
        this._onKeyDown = (event) => {
            if (event.key === "Enter") {
                event.preventDefault(); // evita comportamiento por defecto
                this._handleEnterSearch();
            }
        };

        // Se activa cuando el POS ya está en pantalla
        onMounted(() => {
            document.addEventListener("keydown", this._onKeyDown);
        });

        // Se limpia cuando salís de la pantalla
        onWillUnmount(() => {
            document.removeEventListener("keydown", this._onKeyDown);
        });
    },

    // ==================================================
    // 🔹 CUANDO PRESIONAN ENTER EN EL BUSCADOR
    // ==================================================
    _handleEnterSearch() {
        const word = this.pos.searchProductWord?.trim();

        // Si no hay texto, no hacemos nada
        if (!word) return;

        console.log("⏎ [POS] Enter detectado con:", word);

        // Buscar producto por Referencia Interna
        const product = this.pos.models["product.product"].find(
            (p) => p.default_code === word
        );

        // Si no existe, avisamos
        if (!product) {
            console.warn("❌ Producto no encontrado:", word);
            return;
        }

        // Agregar producto a la factura
        this.pos.addLineToCurrentOrder({ product_id: product });

        // Limpiar buscador y buffer
        this.pos.searchProductWord = "";
        this.numberBuffer.reset();
    },

    // ==================================================
    // 🔹 CUANDO ESCANEAN UN CÓDIGO DE BARRAS
    // ==================================================
    async _barcodeProductAction(code) {
        console.log("📦 [POS] Escaneo detectado:", code);

        const product = this.pos.models["product.product"].find(
            (p) => p.default_code === code
        );

        if (!product) {
            console.warn("❌ Producto no encontrado por escaneo:", code);
            this.barcodeReader.showNotFoundNotification(code);
            return;
        }

        console.log("✅ Producto agregado por escaneo:", product.display_name);

        await this.pos.addLineToCurrentOrder(
            { product_id: product },
            { code }
        );

        this.numberBuffer.reset();
    },

    // ==================================================
    // 🔹 BUSCADOR NORMAL (NO TOCAMOS SU COMPORTAMIENTO)
    // ==================================================
    get searchWord() {
        return this.pos.searchProductWord || "";
    },
});