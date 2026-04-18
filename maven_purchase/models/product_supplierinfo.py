# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    unit_rate = fields.Float(string="Unit Rate")