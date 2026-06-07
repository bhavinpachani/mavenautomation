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


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.constrains('ref', 'partner_id', 'move_type', 'company_id')
    def _check_unique_vendor_bill_ref(self):
        for move in self:
            if move.move_type != 'in_invoice' or not move.ref:
                continue

            duplicate = self.search_count([
                ('move_type', '=', 'in_invoice'),
                ('company_id', '=', move.company_id.id),
                ('partner_id', '=', move.partner_id.id),
                ('ref', '=', move.ref),
                ('state', '!=', 'cancel'),
            ])

            if duplicate > 1:
                raise ValidationError(
                    f"Vendor Bill Reference '{move.ref}' already exists for this vendor."
                )