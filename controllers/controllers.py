# -*- coding: utf-8 -*-
# from odoo import http


# class L10nMxHmExpress1(http.Controller):
#     @http.route('/l10n_mx_hm_express_1/l10n_mx_hm_express_1', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_mx_hm_express_1/l10n_mx_hm_express_1/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_mx_hm_express_1.listing', {
#             'root': '/l10n_mx_hm_express_1/l10n_mx_hm_express_1',
#             'objects': http.request.env['l10n_mx_hm_express_1.l10n_mx_hm_express_1'].search([]),
#         })

#     @http.route('/l10n_mx_hm_express_1/l10n_mx_hm_express_1/objects/<model("l10n_mx_hm_express_1.l10n_mx_hm_express_1"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_mx_hm_express_1.object', {
#             'object': obj
#         })

