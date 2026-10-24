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
* Creates purchase.order.line on the current order only when every row is valid
* Matches Product, Unit, Pur. For and Taxes without checking letter case
* Does not import any line when the sheet still has unmatched values
* Downloads not_imported.xls with unmatched values shown in red
    """,
    'author': '',
    'website': '',
    'depends': [
        'purchase',
        'maven_purchase',
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
