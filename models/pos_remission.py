# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PosRemission(models.Model):
    _name = 'pos.remission'
    _description = "Remisiones del Point of Sale"

    product_id = fields.Many2one('product.product', string="Producto")
    qty = fields.Float(string="Cantidad", copy=False, default=0.0)
    pending_billing_amount = fields.Float(string="Pend. Facturar", copy=False, default=0.0)
    average_cost_amount = fields.Float(string="Costo promedio", copy=False, default=0.0)
    total_pending_billing = fields.Float(string="Total pendiente de facturar", copy=False, default=0.0)

    @api.model
    def new_lines_create(self, lines_data):
        """
        Método de clase para crear líneas de remisión
        Si el producto ya existe, suma los valores en lugar de crear nueva línea
        """
        print(f"📥 Recibiendo {len(lines_data)} líneas para procesar \n toda la linea {lines_data}")
        
        try:
            created_count = 0
            updated_count = 0
            
            for line in lines_data:
                product_id_js = line.get('product_id')
                
                # Saltar si no hay product_id válido
                if not product_id_js:
                    print(f"⚠️ Saltando línea sin product_id válido: {line}")
                    continue
                
                product_id = self.env['product.product'].search([('id', '=', product_id_js)])
                # Buscar si ya existe una remisión para este producto
                existing_remission = self.search([('product_id', '=', product_id.id)], limit=1)
                
                if existing_remission:
                    # Si existe, actualizar sumando los valores
                    new_qty = existing_remission.qty + line.get('qty', 0)
                    new_pending = existing_remission.pending_billing_amount + line.get('qty') if line.get('state') != 'invoiced' else existing_remission.pending_billing_amount + 0
                    new_total_pending = existing_remission.total_pending_billing + (line.get('qty') * product_id.lst_price) if line.get('state') != 'invoiced' else existing_remission.total_pending_billing + 0
                    
                    existing_remission.write({
                        'qty': new_qty,
                        'pending_billing_amount': new_pending,
                        'average_cost_amount': product_id.standard_price,
                        'total_pending_billing': new_total_pending,
                    })
                    
                    updated_count += 1
                    print(f"🔄 Línea actualizada para producto ID: {product_id}")
                    print(f"   Cantidad: {existing_remission.qty - line.get('qty', 0)} → {new_qty}")
                    print(f"   Pend. Facturar: {existing_remission.pending_billing_amount - line.get('price_subtotal', 0)} → {new_pending}")
                    
                else:
                    # Si no existe, crear nueva remisión

                    self.create({
                        'product_id': product_id.id,
                        'qty': line.get('qty', 0),
                        'pending_billing_amount': line.get('qty') if line.get('state') != 'invoiced' else 0,
                        'average_cost_amount': product_id.standard_price,
                        'total_pending_billing': line.get('qty') * product_id.lst_price if line.get('state') != 'invoiced' else 0,
                    })
                    created_count += 1
                    print(f"✅ Nueva línea creada para producto ID: {product_id}")
            
            print(f"📊 Resumen - Creadas: {created_count}, Actualizadas: {updated_count}")
            return {
                'success': True, 
                'created_count': created_count, 
                'updated_count': updated_count,
                'total_processed': created_count + updated_count
            }
            
        except Exception as e:
            print(f"❌ Error al procesar líneas: {str(e)}")
            return {'success': False, 'error': str(e)}
        
    def action_open_create_sale_order_wizard(self):
        """
        Abre el wizard para crear una orden de venta a partir de las remisiones seleccionadas.
        """
        # El active_ids se pasa automáticamente al default_get del wizard
        return {
            'name': "Crear Orden de Venta desde Remisiones",
            'type': 'ir.actions.act_window',
            'res_model': 'pos.remission.wizard',
            'view_mode': 'form',
            'target': 'new',  # Abre la vista como un diálogo (wizard)
            'context': self.env.context,
        }