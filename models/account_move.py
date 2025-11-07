# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_note_custom = fields.Boolean(
        string="Nota de remisión", 
        default=False, 
        copy=False,
        help="Habilita la gestión de inventario mediante notas de remisión",
        tracking=True
    )

    def action_post(self):
        """Extiende la validación de facturas para manejar notas de remisión"""
        res = super().action_post()

        for move in self:
            for line in move.invoice_line_ids:
                product = line.product_id
                qty = line.quantity

                # Buscar remisión del producto
                remission = self.env['pos.remission'].search([('product_id', '=', product.id)], limit=1)

                # Si la factura es NOTA DE REMISIÓN, SUMA la cantidad pendiente
                if move.delivery_note_custom:
                    if remission:
                        remission.pending_billing_amount += qty
                    else:
                        self.env['pos.remission'].create({
                            'product_id': product.id,
                            'qty': 0.0,
                            'pending_billing_amount': qty,
                            'average_cost_amount': line.product_id.lst_price,
                        })
                else:
                    # Si NO es nota de remisión, RESTA (porque se está facturando algo pendiente)
                    if remission:
                        remission.pending_billing_amount -= qty
                        if remission.pending_billing_amount < 0:
                            remission.pending_billing_amount = 0
                    else:
                        # Si no existe registro, podrías decidir crear uno con negativo o lanzar error
                        # Aquí mejor lo dejamos en 0 por seguridad
                        self.env['pos.remission'].create({
                            'product_id': product.id,
                            'qty': 0.0,
                            'pending_billing_amount': 0.0,
                            'average_cost_amount': line.product_id.lst_price,
                        })
        return res

    def button_cancel(self):
        """Maneja la cancelación de facturas con notas de remisión"""
        res = super().button_cancel()

        for move in self:
            for line in move.invoice_line_ids:
                product = line.product_id
                qty = line.quantity

                remission = self.env['pos.remission'].search([('product_id', '=', product.id)], limit=1)
                if remission:
                    # Si la factura era NOTA DE REMISIÓN, revertir sumando → restar
                    if move.delivery_note_custom:
                        remission.pending_billing_amount -= qty
                        if remission.pending_billing_amount < 0:
                            remission.pending_billing_amount = 0
                    else:
                        # Si era factura normal, revertir la resta → sumar
                        remission.pending_billing_amount += qty
        return res
