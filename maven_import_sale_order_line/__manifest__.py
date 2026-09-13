# -*- coding: utf-8 -*-
{
    'name': 'Import Sale Order Lines',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Import sale order lines from Excel or CSV into an existing draft quotation',
    'description': """
Import Sale Order Lines
=======================
* Import SOL button on draft sale orders
* Upload XLS / CSV with Product, Quantity, Unit, Del. Time, LP, Disc.%, Unit Rate, Amount, Taxes
* Creates sale.order.line on the current order only
* Skips already imported products
* Downloads not_imported.xls with red/green highlighting for product and taxes
    """,
    'author': '',
    'website': '',
    'depends': [
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_sale_order_line_views.xml',
        'views/sale_order_views.xml',
    ],
    'external_dependencies': {
        'python': ['xlrd', 'xlwt'],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
