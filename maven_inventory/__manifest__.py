# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Maven Inventory',
    'version': '1.0',
    'category': 'Inventory',
    'description': """
                Inventory
    """,
    'depends': ['base', 'purchase', 'maven_accounting', 'stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inventory_type_views.xml',
        'views/product_views.xml',
        'views/product_removal_view.xml',
        'views/stock_move_view.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'maven_inventory/static/src/stock_forecasted/**/*',
        ],
    },
    'auto_install': True,
    'author': 'Odoo S.A.',
    'license': 'LGPL-3',
}

