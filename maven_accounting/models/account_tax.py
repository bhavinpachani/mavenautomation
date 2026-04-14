# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_default_tax = fields.Boolean(string="Default Tax")