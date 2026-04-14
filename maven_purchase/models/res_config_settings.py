# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # terms_purchase_note = fields.Text(
    #     "Terms & Conditions",
    #     config_parameter='mavenautomation.terms_purchase_note'
    # )
    #
    # is_purchase_note = fields.Boolean(
    #     "Purchase Terms & Conditions",
    #     config_parameter='mavenautomation.is_purchase_note'
    # )

    validate_po_vat = fields.Boolean(
        "Vat",
        config_parameter='mavenautomation.validate_po_vat'
    )

    validate_po_email = fields.Boolean(
        "Email",
        config_parameter='mavenautomation.validate_po_email'
    )

    validate_po_mobile = fields.Boolean(
        "Mobile",
        config_parameter='mavenautomation.validate_po_mobile'
    )

    validate_po_payment_term = fields.Boolean(
        "Payment Term",
        config_parameter='mavenautomation.validate_po_payment_term'
    )

    validate_po_address = fields.Boolean(
        "Address",
        config_parameter='mavenautomation.validate_po_address'
    )

    validate_po_tag = fields.Boolean(
        "Deal In",
        config_parameter='mavenautomation.validate_po_tag'
    )

    validate_po_industry_id = fields.Boolean(
        string="Contact Type",
        config_parameter='mavenautomation.validate_po_industry_id'
    )