# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Maven Automation Purchase',
    'description': 'Maven Automation Purchase',
    'summary': 'Maven Automation',
    'category': 'Purchase/Purchase',
    'sequence': 1,
    'version': '19.0.0.0',
    'author': 'Maven Automation Purchase',
    'website': 'https://www.mavenautomation.in',
    'depends': [
        'purchase',
        'delivery'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_for_view.xml',
        'views/purchase_report_view .xml',
        'views/product_supplierinfo_view.xml',
        'views/purchase_order_view.xml',
        'views/res_config_settings_view.xml',
        'views/purchase_history_view.xml',
        'views/purchase_order_report.xml'

    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
