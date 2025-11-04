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
        
        orders_with_remission = self.filtered(lambda o: o.delivery_note_custom)
        if not orders_with_remission:
            return res

        # Optimización: obtener todos los productos de una vez
        all_product_ids = orders_with_remission.mapped('order_line.product_id').ids
        
        # Buscar todas las remisiones existentes en una sola consulta
        existing_remissions = self.env['pos.remission'].search([
            ('product_id', 'in', all_product_ids)
        ])
        remission_by_product = {r.product_id.id: r for r in existing_remissions}
        
        # Preparar datos para creación/actualización
        remission_vals_list = []
        
        for order in orders_with_remission:
            for line in order.order_line:
                if not line.product_id:
                    continue
                    
                product_id = line.product_id.id
                remission = remission_by_product.get(product_id)
                
                if remission:
                    # Actualizar remisión existente
                    remission.qty += line.product_uom_qty
                    remission.pending_billing_amount += line.product_uom_qty
                    remission.average_cost_amount = line.product_id.standard_price
                else:
                    # Preparar para crear nueva remisión
                    remission_vals_list.append({
                        'product_id': product_id,
                        'qty': line.product_uom_qty,
                        'pending_billing_amount': line.product_uom_qty,
                        'average_cost_amount': line.product_id.standard_price,
                    })
                    # Actualizar el diccionario para evitar duplicados en la misma ejecución
                    remission_by_product[product_id] = None
        
        # Crear nuevas remisiones en lote
        if remission_vals_list:
            self.env['pos.remission'].create(remission_vals_list)
            
        return res

    def action_cancel(self):
        """Maneja la cancelación de órdenes con notas de remisión"""
        res = super().action_cancel()
        
        orders_with_remission = self.filtered(lambda o: o.delivery_note_custom)
        if not orders_with_remission:
            return res

        # Optimización similar a action_confirm
        all_product_ids = orders_with_remission.mapped('order_line.product_id').ids
        existing_remissions = self.env['pos.remission'].search([
            ('product_id', 'in', all_product_ids)
        ])
        remission_by_product = {r.product_id.id: r for r in existing_remissions}
        
        remissions_to_unlink = self.env['pos.remission']
        
        for order in orders_with_remission:
            for line in order.order_line:
                if not line.product_id:
                    continue
                    
                remission = remission_by_product.get(line.product_id.id)
                if not remission:
                    continue
                    
                new_qty = remission.qty - line.product_uom_qty
                new_pending_billing_amount = remission.pending_billing_amount - line.product_uom_qty
                
                if new_qty <= 0:
                    # Recolectar para eliminar después (evita modificar durante iteración)
                    remissions_to_unlink |= remission
                else:
                    remission.qty = new_qty
                    remission.pending_billing_amoount = new_pending_billing_amount
        
        # Eliminar en lote
        if remissions_to_unlink:
            remissions_to_unlink.unlink()
            
        return res

    @api.model
    def _get_remission_for_products(self, product_ids):
        """Método helper para obtener remisiones por productos"""
        return self.env['pos.remission'].search([
            ('product_id', 'in', list(product_ids))
        ])
    
    @api.depends('invoice_ids')
    def set_delivery_note_custom(self):
        for order in self:
            print("se esta creando una factura apartir de la orden de venta") 
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    invoice.delivery_note_custom = True