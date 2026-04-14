# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_roundoff = fields.Boolean(
        string='Allow rounding of invoice amount',
        help="Allow rounding of invoice amount",
        config_parameter='account.invoice_roundoff'
    )

    roundoff_account_id = fields.Many2one(
        'account.account',
        string='Roundoff Account',
        config_parameter='account.roundoff_account_id'
    )