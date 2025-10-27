# -*- coding: utf-8 -*-

from odoo import models, fields

class PosSession(models.Model):
    _inherit = 'pos.session'

    def _pos_ui_models_to_load(self):
        result = super()._pos_ui_models_to_load()
        result.append('pos.order')
        return result

    def _loader_params_pos_order(self):
        return {
            'search_params': {
                'domain': [],
                'fields': ['delivery_note_custom', 'amount_total_words'],
            },
        }

    def _get_pos_ui_pos_order(self, params):
        return self.env['pos.order'].search_read(**params['search_params'])