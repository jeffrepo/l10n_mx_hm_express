# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import re



class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_note_custom = fields.Boolean(string="Nota de remisión", default=False, copy=False, tracking=True)
    amount_total_words = fields.Char(string="Total en letras", default=False, copy=False)



    # def get_qr_link(self):
    #     self.ensure_one()
    #     cfdi_infos = self.env['l10n_mx_edi.document']._decode_cfdi_attachment(self.l10n_mx_edi_cfdi_attachment_id.raw)
    #     if not cfdi_infos:
    #         return {}

    #     barcode_value_params = keep_query(
    #         id=cfdi_infos['uuid'],
    #         re=cfdi_infos['supplier_rfc'],
    #         rr=cfdi_infos['customer_rfc'],
    #         tt=cfdi_infos['amount_total'],
    #     )
    #     barcode_sello = url_quote_plus(cfdi_infos['sello'][-8:], safe='=/').replace('%2B', '+')
    #     barcode_value = url_quote_plus(f'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?{barcode_value_params}&fe={barcode_sello}')
    #     barcode_src = f'/report/barcode/?barcode_type=QR&value={barcode_value}&width=180&height=180'

    #     return barcode_src
    
    @api.model
    def get_mx_cfdi_ticket_data_by_uuid(self, uuid):
        logging.warning("get_mx_cfdi_ticket_data_by_uuid")
        logging.warning(uuid)
        order = self.search([("uuid", "=", uuid)], limit=1)
        logging.warning(order)
        logging.warning(order.account_move)
        if not order or not order.account_move:
            return {}
        move = order.account_move
        cfdi_value = order.account_move._l10n_mx_edi_get_extra_invoice_report_values()
        logging.warning(cfdi_value)
        if not cfdi_value:
            return {}
        partner = move.partner_id
        no_cert_sat = getattr(move, "l10n_mx_edi_sat_cert_number", False) or ""
        no_cert_emisor = getattr(move, "l10n_mx_edi_cfdi_cert_number", False) or ""
        fecha_certificacion = cfdi_value["stamp_date"]
        # Datos “forma/metodo/uso/moneda” (ajusta a tus campos reales)
        forma_pago = getattr(move, "l10n_mx_edi_payment_method_id", False)
        metodo_pago = getattr(move, "l10n_mx_edi_payment_policy", False)
        uso_cfdi = getattr(move, "l10n_mx_edi_usage", False)
        no_cert_emisor = cfdi_value["certificate_number"]
        no_cert_sat = cfdi_value["certificate_sat_number"]
        # “Cadena digital” depende de implementación; a veces está en un campo EDI o en el XML
        cadena_digital = cfdi_value["cadena"]
        sello_digital_cfdi = cfdi_value["sello"]
        sello_digital_sat = cfdi_value["sello_sat"]
        forma = ""
        cantidad_letra = move.amount_total_words
        extra_values = move._l10n_mx_edi_get_extra_common_report_values()
        logging.warning(extra_values)
        if not move.l10n_mx_edi_cfdi_uuid:
            return {}
        # aquí devuelves lo que quieras imprimir (uuid, fecha timbrado, certificados, cadena, etc.)
        return {
            "invoice_name": move.name or "",
            "folio_ref": order.pos_reference or "",
            "fecha_emision": move.invoice_date.strftime("%d/%m/%Y") if move.invoice_date else "",
            "fecha_certificacion": fecha_certificacion,
            "expedido_en": (move.company_id.city or "") + (", " + (move.company_id.state_id.name or "") if move.company_id.state_id else ""),
            "cliente_nombre": partner.name or "",
            "cliente_rfc": partner.vat or "",
            "cliente_domicilio": partner.contact_address or "",
            "uuid": uuid,
            "no_cert_sat": no_cert_sat,
            "no_cert_emisor": no_cert_emisor,
            "forma_pago_cliente": forma_pago.display_name if forma_pago else "",
            "metodo_pago": metodo_pago or "",
            "uso_cfdi": uso_cfdi or "",
            "moneda": move.currency_id.name or "",
            "cadena_digital": cadena_digital or "",
            "cantidad_letra": cantidad_letra or "",
            "sello_digital_cfdi": sello_digital_cfdi or "",
            "sello_digital_sat": sello_digital_sat or "",
            "extra_values": extra_values or "",
        }
    
    @api.model
    def get_amount_total_words(self, total, currency_id):
        """Convierte un monto a letras usando la moneda indicada"""
        print(f"el total {total}, el id de la moneda {currency_id}")
        currency = self.env['res.currency'].browse(currency_id)
        print(f"la moneda {currency}")
        self.amount_total_words = currency.amount_to_text(total).replace(',', '')
        return currency.amount_to_text(total).replace(',', '')

    # @api.model
    # def get_mx_cfdi_ticket_data_by_uid(self, uid):
    #     order = self.search([("uid", "=", uid)], limit=1)
    #     if not order:
    #         return {}

    #     move = order.account_move  # factura del POS (ajusta si la guardas en otro campo)
    #     if not move:
    #         return {}

    #     # Si aún no está timbrada, probablemente no hay UUID
    #     uuid = getattr(move, "l10n_mx_edi_cfdi_uuid", False)
    #     if not uuid:
    #         return {}

    #     partner = move.partner_id

    #     # Campos típicos l10n_mx_edi (pueden variar según tu módulo)
    #     no_cert_sat = getattr(move, "l10n_mx_edi_sat_cert_number", False) or ""
    #     no_cert_emisor = getattr(move, "l10n_mx_edi_cfdi_cert_number", False) or ""

    #     # “Cadena digital” depende de implementación; a veces está en un campo EDI o en el XML
    #     cadena_digital = getattr(move, "l10n_mx_edi_cfdi_cadena_original", False) or ""

    #     # Datos “forma/metodo/uso/moneda” (ajusta a tus campos reales)
    #     forma_pago = getattr(move, "l10n_mx_edi_payment_method_id", False)
    #     metodo_pago = getattr(move, "l10n_mx_edi_payment_policy", False)
    #     uso_cfdi = getattr(move, "l10n_mx_edi_usage", False)

    #     return {
    #         "invoice_name": move.name or "",
    #         "folio_ref": order.pos_reference or "",
    #         "fecha_emision": move.invoice_date.strftime("%d/%m/%Y") if move.invoice_date else "",
    #         "fecha_certificacion": move.l10n_mx_edi_cfdi_datetime.strftime("%Y-%m-%dT%H:%M:%S") if getattr(move, "l10n_mx_edi_cfdi_datetime", False) else "",
    #         "expedido_en": (move.company_id.city or "") + (", " + (move.company_id.state_id.name or "") if move.company_id.state_id else ""),
    #         "cliente_nombre": partner.name or "",
    #         "cliente_rfc": partner.vat or "",
    #         "cliente_domicilio": partner.contact_address or "",
    #         "uuid": uuid,
    #         "no_cert_sat": no_cert_sat,
    #         "no_cert_emisor": no_cert_emisor,
    #         "forma_pago_cliente": forma_pago.display_name if forma_pago else "",
    #         "metodo_pago": metodo_pago or "",
    #         "uso_cfdi": uso_cfdi or "",
    #         "moneda": move.currency_id.name or "",
    #         "cadena_digital": cadena_digital or "",
    #     }


    # @api.model
    # def _process_order(self, order, existing_order):
    #     res = super()._process_order(order, existing_order)

    #     # res puede ser int (id) o recordset según el super en tu stack
    #     pos_order = self.browse(res) if isinstance(res, int) else res

    #     # --- tu lógica de timbrado aquí ---
    #     if (
    #         pos_order
    #         and pos_order.company_id.country_id.code == "MX"
    #         and pos_order.to_invoice
    #         and pos_order.account_move
    #     ):
    #         move = pos_order.account_move
    #         if move.state != "posted":
    #             move.action_post()

    #         try:
    #             move._l10n_mx_edi_cfdi_invoice_try_send()
    #         except Exception as e:
    #             # Si necesitas forzar timbrado:
    #             raise UserError(_("No se pudo timbrar automáticamente la factura. Detalle: %s") % str(e))

    #     # 🔥 CLAVE: devolver EXACTAMENTE lo que devolvió super()
    #     return res




    @api.model
    def sync_from_ui(self, orders):
        data = super().sync_from_ui(orders)

        pos_rows = (data or {}).get("pos.order", [])
        if not pos_rows:
            _logger.warning("POS autostamp: sin pos.order en retorno; no se timbra nada.")
            return data

        # ⚠️ IMPORTANTÍSIMO: solo órdenes que en ESTE retorno tienen account_move
        # y todavía no tienen uuid CFDI
        move_ids = []
        for row in pos_rows:
            # row viene como dict (como en tu log)
            if row.get("account_move") and not row.get("l10n_mx_edi_cfdi_uuid"):
                move_ids.append(row["account_move"])

        if not move_ids:
            _logger.warning("POS autostamp: no hay account_move nuevos/pendientes en este retorno; no se timbra.")
            return data

        moves = self.env["account.move"].browse(move_ids)

        for move in moves:
            # Ya timbrada por otro proceso
            if move.l10n_mx_edi_cfdi_uuid:
                continue

            if move.state != "posted":
                move.action_post()

            partner = move.partner_id
            vat = (partner.vat or "").strip().upper()
            name = (partner.name or "").strip().upper()
            
            # Decide tu política:
            # - si el POS es mostrador y normalmente es público general:
            #if vat == "XAXX010101000" or "PUBLICO EN GENERAL" in name:
            move.l10n_mx_edi_cfdi_to_public = True
            move._l10n_mx_edi_cfdi_invoice_try_send()
            doc = self.env["l10n_mx_edi.document"].search(
                [("move_id", "=", move.id)], order="id desc", limit=1
            )
            
            _logger.warning(
                "RESULTADO TIMBRADO POS -> %s uuid=%s cfdi_state=%s doc_state=%s msg=%s",
                move.name,
                move.l10n_mx_edi_cfdi_uuid,
                move.l10n_mx_edi_cfdi_state,
                getattr(doc, "state", None),
                (doc.message or "")[:200],
)
            if not move.l10n_mx_edi_cfdi_uuid:
                doc = self.env["l10n_mx_edi.document"].search(
                    [("move_id", "=", move.id)],
                    order="id desc",
                    limit=1
                )
                msg = doc.message if doc and doc.message else _("Sin detalle de error.")
                raise UserError(_("No se pudo timbrar la factura %s.\nDetalle: %s") % (move.name, msg))

        return data