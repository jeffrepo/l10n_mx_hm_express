# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class PosRemission(models.Model):
    _name = 'pos.remission'
    _description = "Remisiones del Point of Sale"

    product_id = fields.Many2one('product.product', string="Producto")
    qty = fields.Float(string="Cantidad", copy=False, default=0.0)
    pending_billing_qty = fields.Float(string="Pend. Facturar", copy=False, default=0.0)
    average_cost_amount = fields.Float(string="Costo promedio", copy=False, default=0.0)

    total_pending_billing = fields.Float(
        string="Total pendiente de facturar",
        compute="_compute_total_pending_billing",
        store=True,
        copy=False
    )

    @api.depends('pending_billing_qty', 'average_cost_amount')
    def _compute_total_pending_billing(self):
        """Calcula automáticamente el total pendiente según cantidad * precio"""
        for rec in self:
            if rec.product_id:
                rec.total_pending_billing = rec.pending_billing_qty * rec.average_cost_amount
            else:
                rec.total_pending_billing = 0.0

    # ===============================================================
    # 🔧 Lógica principal llamada desde JS (PaymentScreen)
    # ===============================================================
    @api.model
    def new_lines_create(self, lines_data):
        """
        Crea o actualiza líneas de remisión desde el POS.
        Ignora líneas sin producto válido.
        """
        print(f"📥 Recibiendo {len(lines_data)} líneas para procesar \n toda la línea {lines_data}")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        # order_list = []
        try:
            for line in lines_data:
                product_id_js = line.get('product_id')

                # 🧱 Evitar líneas sin producto
                if not product_id_js:
                    skipped_count += 1
                    print(f"⚠️ Línea ignorada (sin producto): {line}")
                    continue

                product_id = self.env['product.product'].browse(product_id_js)
                if not product_id.exists():
                    skipped_count += 1
                    print(f"⚠️ Línea ignorada (producto no existe): {line}")
                    continue

                # Buscar si ya existe una remisión
                existing_remission = self.search([('product_id', '=', product_id.id)], limit=1)

                #Vamos a buscar si tiene factura y colocarle remision
                # if line.get('order_id') and line.get('order_id') not in order_list:
                #     order = self.env['pos.order'].search([('id', '=', line.get('order_id'))])
                #     if order.account_move:
                #         order.account_move.delivery_note_custom = True
                #         order_list.append(
                #             line.get('order_id')
                #         )

                if existing_remission:
                    new_qty = existing_remission.qty + line.get('qty', 0)
                    new_pending = existing_remission.pending_billing_qty + line.get('qty')
                    

                    existing_remission.write({
                        'qty': new_qty,
                        'pending_billing_qty': new_pending,
                        'average_cost_amount': product_id.standard_price,
                    })
                    updated_count += 1

                else:
                    self.create({
                        'product_id': product_id.id,
                        'qty': line.get('qty'),
                        'pending_billing_qty': line.get('qty'),
                        'average_cost_amount': product_id.standard_price,
                    })
                    created_count += 1

            print(f"📊 Resumen - Creadas: {created_count}, Actualizadas: {updated_count}, Ignoradas: {skipped_count}")

            return {
                'success': True,
                'created_count': created_count,
                'updated_count': updated_count,
                'skipped_count': skipped_count,
                'total_processed': created_count + updated_count,
            }

        except Exception as e:
            print(f"❌ Error al procesar líneas: {str(e)}")
            return {'success': False, 'error': str(e)}


        
    def action_open_create_account_move_wizard(self):
        """
        Abre el wizard para crear una orden de venta a partir de las remisiones seleccionadas.
        """
        # El active_ids se pasa automáticamente al default_get del wizard
        return {
            'name': "Crear factura desde Remisiones",
            'type': 'ir.actions.act_window',
            'res_model': 'pos.remission.wizard',
            'view_mode': 'form',
            'target': 'new',  # Abre la vista como un diálogo (wizard)
            'context': self.env.context,
        }