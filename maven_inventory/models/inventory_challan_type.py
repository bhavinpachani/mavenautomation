# -*- coding: utf-8 -*-

from odoo import api, fields, models


class InventoryChallanType(models.Model):
    _name = 'inventory.challan.type'
    _description = 'Challan Type'
    _order = 'name, id'

    name = fields.Char(string='Name', required=True)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            self.name = self.name.strip().upper()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].strip().upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].strip().upper()
        return super().write(vals)

    _name_uniq = models.Constraint(
        'unique (name)',
        'Challan Type already exists.',
    )
