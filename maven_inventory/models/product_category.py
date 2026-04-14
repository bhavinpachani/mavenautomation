# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")

    @api.model
    def default_get(self, fields):
        res = super(ProductCategory, self).default_get(fields)
        product_removal_id = self.env['product.removal'].search([
            ('is_default', '=', True)
        ])

        if product_removal_id:
            res['removal_strategy_id'] = product_removal_id.id

        res['property_cost_method'] = 'standard'
        res['property_valuation'] = 'real_time'
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].upper()
        return super().write(vals)