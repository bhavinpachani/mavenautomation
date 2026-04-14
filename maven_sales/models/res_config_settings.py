# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    validate_so_vat = fields.Boolean(
        string="VAT",
        config_parameter="mavenautomation.validate_so_vat"
    )
    validate_so_email = fields.Boolean(
        string="Email",
        config_parameter="mavenautomation.validate_so_email"
    )
    validate_so_mobile = fields.Boolean(
        string="Mobile",
        config_parameter="mavenautomation.validate_so_mobile"
    )
    validate_so_payment_term = fields.Boolean(
        string="Payment Term",
        config_parameter="mavenautomation.validate_so_payment_term"
    )
    validate_so_salesman = fields.Boolean(
        string="Salesman",
        config_parameter="mavenautomation.validate_so_salesman"
    )
    validate_so_address = fields.Boolean(
        string="Address",
        config_parameter="mavenautomation.validate_so_address"
    )
    validate_so_delivery = fields.Boolean(
        string="Delivery Method",
        config_parameter="mavenautomation.validate_so_delivery"
    )
    validate_so_po = fields.Boolean(
        string="PO Number",
        config_parameter="mavenautomation.validate_so_po"
    )
    validate_so_industry_id = fields.Boolean(
        string="Contact Type",
        config_parameter="mavenautomation.validate_so_industry_id"
    )