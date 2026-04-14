# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    price = fields.Float(string="List Price(LP)")

    @api.constrains('partner_id', 'product_tmpl_id', 'product_id')
    def _check_unique_vendor(self):
        for rec in self:
            if not rec.partner_id or not rec.product_tmpl_id:
                continue

            domain = [
                ('id', '!=', rec.id),
                ('partner_id', '=', rec.partner_id.id),
                ('product_tmpl_id', '=', rec.product_tmpl_id.id),
            ]

            # If you want variant-level restriction
            if rec.product_id:
                domain.append(('product_id', '=', rec.product_id.id))
            else:
                domain.append(('product_id', '=', False))

            duplicate = self.search(domain, limit=1)

            if duplicate:
                raise ValidationError(
                    "This vendor is already assigned to this product!"
                )
