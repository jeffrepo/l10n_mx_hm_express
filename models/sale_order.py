# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_note_custom = fields.Boolean(
        string="Nota de remisión", 
        default=False, 
        copy=False,
        help="Habilita la gestión de inventario mediante notas de remisión",
        tracking=True
    )

    def action_confirm(self):
        """Extiende la confirmación para manejar notas de remisión"""
        res = super().action_confirm()

        for order in self:
            # Solo aplica si la orden tiene la opción de nota de remisión
            if not order.delivery_note_custom:
                continue

            for line in order.order_line:
                product = line.product_id
                qty = line.product_uom_qty

                # Verificar que el producto es válido
                if not product or not product.id:
                    continue

                remission = self.env['pos.remission'].search([
                    ('product_id', '=', product.id)
                ], limit=1)

                if remission:
                    # Si existe, actualizamos las cantidades
                    new_qty = remission.qty + qty
                    new_pending = remission.pending_billing_amount + qty

                    remission.write({
                        'qty': new_qty,
                        'pending_billing_amount': new_pending,
                        'average_cost_amount': product.standard_price,
                    })

                    _msg = f"🔁 Actualizada remisión producto {product.display_name}: +{qty}"
                else:
                    # Si no existe, la creamos
                    self.env['pos.remission'].create({
                        'product_id': product.id,
                        'qty': qty,
                        'pending_billing_amount': qty,
                        'average_cost_amount': product.standard_price,
                    })
                    _msg = f"🆕 Creada nueva remisión para {product.display_name}: {qty}"

                print(_msg)

        return res

    def action_cancel(self):
        """Maneja la cancelación de órdenes con notas de remisión"""
        res = super().action_cancel()

        for order in self:
            if not order.delivery_note_custom:
                continue

            for line in order.order_line:
                product = line.product_id
                qty = line.product_uom_qty

                if not product or not product.id:
                    continue

                remission = self.env['pos.remission'].search([
                    ('product_id', '=', product.id)
                ], limit=1)

                if remission:
                    # Restamos las cantidades y validamos que no queden negativas
                    new_qty = remission.qty - qty
                    new_pending = remission.pending_billing_amount - qty

                    if new_qty < 0:
                        new_qty = 0
                    if new_pending < 0:
                        new_pending = 0

                    remission.write({
                        'qty': new_qty,
                        'pending_billing_amount': new_pending,
                    })

                    print(f"❌ Orden cancelada → Remisión actualizada {product.display_name}: -{qty}")

        return res

    def _create_invoices(self, grouped=False, final=False, date=None):
        """Hereda la creación de facturas para copiar delivery_note_custom a account.move"""
        moves = super()._create_invoices(grouped=grouped, final=final, date=date)

        for order in self:
            # Buscamos las facturas relacionadas al pedido
            related_moves = moves.filtered(lambda m: m.invoice_origin and order.name in m.invoice_origin)
            for move in related_moves:
                move.delivery_note_custom = order.delivery_note_custom

        return moves