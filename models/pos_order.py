# -*- coding: utf-8 -*-
from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_note_custom = fields.Boolean(string="Nota de remisión", default=False, copy=False)
    # amount_total_words = fields.Char(string="Total en letras", compute='_compute_amount_total_words', store=False)

    @api.model
    def get_amount_total_words(self, total, currency_id):
        """Convierte un monto a letras usando la moneda indicada"""
        print(f"el total {total}, el id de la moneda {currency_id}")
        currency = self.env['res.currency'].browse(currency_id)
        print(f"la moneda {currency}")
        return currency.amount_to_text(total).replace(',', '')
