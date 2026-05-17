# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class InventoryType(models.Model):
    _name = 'inventory.type'
    _description = "Product Make"

    name = fields.Char(string="Make")
    is_default_make = fields.Boolean(string="Default Make")

    @api.constrains('name', 'is_default_make')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")
            if self.search_count([('is_default_make', '=', True)]) > 1:
                raise ValidationError("Only one Make can be a default.")
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