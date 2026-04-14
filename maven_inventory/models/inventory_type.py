# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class InventoryType(models.Model):
    _name = 'inventory.type'
    _description = "Product Make"

    name = fields.Char(string="Make")

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")