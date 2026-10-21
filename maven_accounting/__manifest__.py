# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Maven Accounting',
    'version': '1.0',
    'category': 'Accounting',
    'description': """
                Accounting
    """,
    'depends': ['base', 'account', 'sale', 'purchase'],
    'data': [
        'views/account_tax_view.xml',
        'views/account_move_view.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
    ],
    'auto_install': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}
