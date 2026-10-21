# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    tax_ids = fields.Many2many(
        domain="[('type_tax_use', '=', 'sale'), ('country_id', '=', tax_country_id), ('is_searchable', '=', True)]",
    )

    @api.depends('product_id', 'company_id')
    def _compute_tax_ids(self):
        super()._compute_tax_ids()
        for line in self:
            line.tax_ids = line.tax_ids.filtered('is_searchable')
