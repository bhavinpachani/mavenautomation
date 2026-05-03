# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Maven Automation MRP',
    'description': 'Maven Automation MRP',
    'summary': 'Maven Automation',
    'category': 'MRP/MRP',
    'sequence': 1,
    'version': '19.0.0.0',
    'author': 'Maven Automation MRP',
    'website': 'https://www.mavenautomation.in',
    'depends': [
        'mrp',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/verify_bom_wizard_view.xml',
        'views/product_template_view.xml',
        'views/mrp_production_view.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}
