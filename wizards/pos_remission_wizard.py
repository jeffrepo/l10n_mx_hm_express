# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class PosRemissionWizard(models.TransientModel):
    _name = 'pos.remission.wizard'
    _description = "Wizard para crear orden de venta desde remisiones"

    partner_id = fields.Many2one('res.partner', string="Cliente", required=True)
    
    line_ids = fields.One2many(
        'pos.remission.wizard.line', 
        'wizard_id', 
        string='Productos'
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PosRemissionWizard, self).default_get(fields_list)
        
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            return res
            
        remissions = self.env['pos.remission'].browse(active_ids)
        
        # Agrupar productos y sumar cantidades pendientes
        product_qty = {}
        for remission in remissions:
            product_id = remission.product_id.id
            if product_id not in product_qty:
                product_qty[product_id] = 0
            product_qty[product_id] += remission.pending_billing_qty or 0
        
        # Crear líneas del wizard
        line_vals = []
        for product_id, qty in product_qty.items():
            line_vals.append((0, 0, {
                'product_id': product_id,
                'qty': qty,  # valor sugerido por defecto
            }))
        
        res['line_ids'] = line_vals
        
        return res

    def action_create_account_move(self):
        """Crear factura de cliente con los productos seleccionados"""
        self.ensure_one()

        if not self.line_ids:
            raise UserError("No hay productos para crear la factura.")

        active_ids = self.env.context.get('active_ids', [])
        remissions = self.env['pos.remission'].browse(active_ids)

        # El pendiente es una referencia, no un límite para facturar.
        selected_products = remissions.mapped('product_id')
        for line in self.line_ids:
            if line.qty > 0 and line.product_id not in selected_products:
                raise UserError(
                    f"El producto '{line.product_id.display_name}' no pertenece a las remisiones seleccionadas."
                )

        # Crear líneas de factura
        aml_vals = []
        for line in self.line_ids:
            if line.qty > 0:
                aml_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': line.qty,
                }))

        # Crear la factura
        am_vals = {
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            'delivery_note_custom': True,
            'invoice_line_ids': aml_vals,
        }
        
        account_move = self.env['account.move'].create(am_vals)

        # Redirigir a la factura creada
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': account_move.id,
            'view_mode': 'form',
            'target': 'current',
            'context': self.env.context,
        }


class PosRemissionWizardLine(models.TransientModel):
    _name = 'pos.remission.wizard.line'
    _description = "Líneas del wizard de remisiones"
    
    wizard_id = fields.Many2one('pos.remission.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Producto')
    qty = fields.Float(string="Cantidad", required=True, default=1.0)
