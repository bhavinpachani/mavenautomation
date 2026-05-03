# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    unit_rate = fields.Float(
        string="Unit Rate",
        compute="_compute_unit_rate",
        store=True
    )
    price_unit = fields.Float(string="LP")

    @api.depends('price_unit', 'quantity', 'discount')
    def _compute_unit_rate(self):
        for line in self:
            if line.quantity:
                total_after_discount = line.price_unit * line.quantity * (1 - (line.discount or 0) / 100)
                line.unit_rate = total_after_discount / line.quantity
            else:
                line.unit_rate = line.price_unit