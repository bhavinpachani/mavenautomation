{
    'name': "Odoo - IndiaMart Connector",
    'category': 'Tools',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',

    'summary': "Integrate & Manage your IndiaMart Leads from Odoo.",

    'description': """
Odoo - IndiaMart Connector
==========================
This module allows to integrate Odoo and IndiaMart and manage Leads from Odoo.
Import all the Leads placed by customer on IndiaMart store to Odoo.
    """,

    'author': 'Dhaval Patel, Niraj Pajwani',
    'website': '',

    'depends': [
        'base',
        'crm',
    ],

    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/indiamart_view.xml',
        'views/crm_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
