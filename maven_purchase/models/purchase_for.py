from odoo import models, fields, api
from odoo.exceptions import ValidationError

class PurchaseFor(models.Model):
    _name = 'purchase.for'
    _description = 'Purchase For'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")

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