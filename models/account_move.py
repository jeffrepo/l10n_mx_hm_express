# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_note_custom = fields.Boolean(
        string="Viene de remisión",
        default=False, 
        copy=False,
        help="Indica si la factura fue generada desde una nota de remisión",
        tracking=True
    )

    # === CONFIRMAR FACTURA ===
    def action_post(self):
        
        """Cuando se valida una factura, actualizar las remisiones relacionadas."""
        res = super().action_post()

        for move in self:
            print(f"se esta facturando algo {move.name}, {move.id}")
            # Solo aplicar la lógica si la factura viene de remisión
            if not move.delivery_note_custom:
                continue

            for line in move.invoice_line_ids:
                product = line.product_id
                qty = line.quantity
                if not product:
                    continue

                # Incluir saldos en cero o negativos para permitir facturar de más.
                remission = self.env['pos.remission'].search([
                    ('product_id', '=', product.id)
                ], limit=1)

                if remission:
                    remission.pending_billing_qty -= qty
                else:
                    raise UserError(
                        f"No existe una remisión para el producto '{product.display_name}'."
                    )
        return res

    # === CANCELAR FACTURA ===
    def button_cancel(self):
        """Revertir el descuento en remisiones solo si la factura ya fue confirmada."""
        res = super().button_cancel()

        for move in self:
            print(f"se esta Cancelando alguna factura {move.name}, {move.id}")
            # Solo aplica si viene de remisión y si estaba publicada
            if not move.delivery_note_custom or move.state != 'posted':
                continue

            for line in move.invoice_line_ids:
                product = line.product_id
                qty = line.quantity
                if not product:
                    continue

                remission = self.env['pos.remission'].search([
                    ('product_id', '=', product.id)
                ], limit=1)

                if remission:
                    remission.pending_billing_qty += qty
                    move.message_post(body=(
                        f"Revertido en remisiones: +{qty} unidades del producto {product.display_name}."
                    ))
        return res

