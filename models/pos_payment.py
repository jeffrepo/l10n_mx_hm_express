# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class PosPayment(models.Model):
    _inherit = "pos.payment"

    delivery_note_custom = fields.Boolean(string="Nota de remisión",related='pos_order_id.delivery_note_custom', store=True)