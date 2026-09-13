# -*- coding: utf-8 -*-
{
    'name': 'Import Purchase Order Lines',
    'version': '19.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Import purchase order lines from Excel or CSV into an existing draft RFQ',
    'description': """
Import Purchase Order Lines
===========================
* Import POL button on draft purchase orders
* Upload XLS / CSV with Product, Quantity, Unit, Pur. For, Expected Arrival,
  LP, Disc.%, Unit Rate, Amount, Taxes
* Creates purchase.order.line on the current order only
* Skips already imported lines
* Downloads not_imported.xls with red/green highlighting for product and taxes
    """,
    'author': '',
    'website': '',
    'depends': [
        'purchase',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/import_purchase_order_line_views.xml',
        'views/purchase_order_views.xml',
    ],
    'external_dependencies': {
        'python': ['xlrd', 'xlwt'],
    },
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
