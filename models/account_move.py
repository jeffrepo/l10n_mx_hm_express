# -*- coding: utf-8 -*-
from odoo import models, fields, api

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
        
        invoices_with_remission = self.filtered(lambda inv: inv.delivery_note_custom and inv.move_type in ['out_invoice', 'out_refund'])
        print(f" invoices_with_remission {invoices_with_remission}")
        if not invoices_with_remission:
            return res

        # Optimización: obtener todos los productos de una vez
        all_product_ids = invoices_with_remission.mapped('invoice_line_ids.product_id').ids
        
        # Buscar todas las remisiones existentes en una sola consulta
        existing_remissions = self.env['pos.remission'].search([
            ('product_id', 'in', all_product_ids)
        ])
        remission_by_product = {r.product_id.id: r for r in existing_remissions}
        
        for invoice in invoices_with_remission:
            for line in invoice.invoice_line_ids:
                if not line.product_id:
                    continue
                    
                product_id = line.product_id.id
                remission = remission_by_product.get(product_id)
                
                if remission:
                    # Actualizar remisión existente - RESTAR cantidad facturada
                    qty_to_update = line.quantity
                    if invoice.move_type == 'out_refund':
                        # Si es nota de crédito, sumamos al pendiente
                        remission.pending_billing_amount += qty_to_update
                    else:
                        # Si es factura normal, restamos del pendiente
                        remission.pending_billing_amount -= qty_to_update
                    
                    # Actualizar costo promedio si es necesario
                    remission.average_cost_amount = line.product_id.standard_price
            
        return res

    def button_cancel(self):
        """Maneja la cancelación de facturas con notas de remisión"""
        res = super().button_cancel()
        
        invoices_with_remission = self.filtered(lambda inv: inv.delivery_note_custom and inv.move_type in ['out_invoice', 'out_refund'])
        if not invoices_with_remission:
            return res

        # Optimización similar a action_post
        all_product_ids = invoices_with_remission.mapped('invoice_line_ids.product_id').ids
        existing_remissions = self.env['pos.remission'].search([
            ('product_id', 'in', all_product_ids)
        ])
        remission_by_product = {r.product_id.id: r for r in existing_remissions}
        
        for invoice in invoices_with_remission:
            for line in invoice.invoice_line_ids:
                if not line.product_id:
                    continue
                    
                remission = remission_by_product.get(line.product_id.id)
                if not remission:
                    continue
                
                qty_to_update = line.quantity
                if invoice.move_type == 'out_refund':
                    # Cancelar nota de crédito: RESTAR del pendiente
                    remission.pending_billing_amount -= qty_to_update
                else:
                    # Cancelar factura: SUMAR al pendiente
                    remission.pending_billing_amount += qty_to_update
            
        return res