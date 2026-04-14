# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Maven Automation Sales',
    'description': 'Maven Automation Sales',
    'summary': 'Maven Automation',
    'category': 'Sales/Sales',
    'sequence': 1,
    'version': '19.0.0.0',
    'author': 'Maven Automation Sales',
    'website': 'https://www.mavenautomation.in',
    'depends': [
        'sale_management',
        'delivery'
    ],
    'data': [
        'views/sale_order_view.xml',
        'views/res_config_settings_view.xml',
        'views/sale_order_report.xml'

    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
