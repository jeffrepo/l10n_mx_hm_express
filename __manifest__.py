# -*- coding: utf-8 -*-
{
    'name': "l10n_mx_hm_express",
    'summary': "Agrega botón de Nota Remisión en POS",
    'description': """
    Extiende la pantalla de punto de venta para agregar un botón de 'Nota Remisión'
    """,
    'author': "SISPAV",
    'website': "https://www.yourcompany.com",
    'category': 'Point of Sale',
    'version': '0.1',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'sale'],
    
    'data': [
        'security/ir.model.access.csv',
        'reports/pos_order_remission_format_pdf_views.xml',
        'reports/report_action.xml',
        'views/account_move_views.xml',
        'views/pos_remission_views.xml',  
        'views/point_of_sale_view.xml',
        'views/pos_order_views.xml',
        'views/sale_menus.xml',
        'views/sale_order_views.xml',
        'wizards/pos_remission_wizard_views.xml'
    ],

    'assets': {
        'point_of_sale._assets_pos': [
            # JS
            'l10n_mx_hm_express/static/src/app/models/pos_order.js',
            'l10n_mx_hm_express/static/src/app/screens/product_screen/control_buttons/nota_remision_button.js',
            'l10n_mx_hm_express/static/src/app/screens/product_screen/control_buttons/control_buttons.js',
            'l10n_mx_hm_express/static/src/app/screens/payment_screen/payment_screen.js',
            'l10n_mx_hm_express/static/src/app/screens/receipt_screen/receipt/order_receipt.js',
            'l10n_mx_hm_express/static/src/js/pos_product_screen_patch.js',
            
            # XML
            'l10n_mx_hm_express/static/src/app/screens/product_screen/control_buttons/control_buttons_template.xml',
            'l10n_mx_hm_express/static/src/app/screens/receipt_screen/receipt/receipt_header/receipt_header.xml',
            'l10n_mx_hm_express/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',

            'l10n_mx_hm_express/static/src/js/pos_receipt_cfdi.js',
            'l10n_mx_hm_express/static/src/js/payment_cfdi_fetch.js',
            'l10n_mx_hm_express/static/src/xml/pos_ticket_cfdi.xml',
        ],
    },
}

