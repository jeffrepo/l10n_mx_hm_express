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
        
        # Agrupar productos y sumar cantidades
        product_qty = {}
        for remission in remissions:
            if remission.product_id.id not in product_qty:
                product_qty[remission.product_id.id] = 0
            product_qty[remission.product_id.id] += remission.qty or 0
        
        # Crear líneas del wizard
        line_vals = []
        for product_id, qty in product_qty.items():
            product = self.env['product.product'].browse(product_id)
            line_vals.append((0, 0, {
                'product_id': product_id,
                'qty': qty,
            }))
        
        res['line_ids'] = line_vals
        
        return res

    def action_create_sale_order(self):
        """Crear orden de venta con los productos seleccionados"""
        self.ensure_one()
        
        if not self.line_ids:
            raise UserError("No hay productos para crear la orden de venta.")
        
        # Prepara las líneas de la orden de venta
        order_lines_vals = []


        for line in self.line_ids:
            if line.qty > 0:
                print(f"line product_id {line.product_id} product_tmplate_id {line.product_id.product_tmpl_id}")
                order_lines_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    # 1. Elimina 'name' o pásalo como False para que Odoo lo calcule
                    # 'name': '', <--- ELIMINAR ESTA LÍNEA
                    'product_uom_qty': line.qty,
                    'price_unit': line.product_id.list_price,
                    # 2. Recomendar incluir la unidad de medida, es semi-obligatoria
                    'product_uom': line.product_id.uom_id.id, 
                }))

        # Crear la orden de venta
        sale_order_vals = {
            'partner_id': self.partner_id.id,
            'order_line': order_lines_vals,
        }
        
        sale_order = self.env['sale.order'].create(sale_order_vals)

        # Redirigir a la orden de venta creada
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
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