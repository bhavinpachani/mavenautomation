# -*- coding: utf-8 -*-
{
    'name': 'Maven Standalone Delivery',
    'version': '19.0.1.0.1',
    'category': 'Inventory/Accounting',
    'summary': 'Link done standalone deliveries on customer invoices that are not created from a sales order.',
    'description': """
Link delivery orders that were created directly (not from a sales order)
to a standalone customer invoice.

Selecting a delivery on the invoice marks it as invoiced. Removing it
sets the delivery back to pending.
    """,
    'author': 'Maven',
    'license': 'LGPL-3',
    'depends': ['account', 'sale_stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'application': False,
}
