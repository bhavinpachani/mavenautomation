# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    inv_type_id = fields.Many2one('inventory.type', string="Make")
    list_price = fields.Float(string="Sales LP", tracking=True)
    purchase_lp_price = fields.Float(string="Purchase LP", tracking=True)

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        sale_taxes = self.env['account.tax'].search([
            ('is_default_tax', '=', True),
            ('type_tax_use', '=', 'sale')
        ])
        purchase_taxes = self.env['account.tax'].search([
            ('is_default_tax', '=', True),
            ('type_tax_use', '=', 'purchase')
        ])

        if sale_taxes:
            res['taxes_id'] = [(6, 0, sale_taxes.ids)]
        if purchase_taxes:
            res['supplier_taxes_id'] = [(6, 0, purchase_taxes.ids)]

        res.update({
            'is_storable': True,
            'tracking': 'none',
            'invoice_policy': 'delivery',
            'purchase_method': 'receive'
        })

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

    x_free_qty = fields.Float(
        string="Free Quantity (Custom)",
        compute="_compute_x_free_qty",
        store=True
    )

    @api.depends('product_variant_ids.free_qty')
    def _compute_x_free_qty(self):
        for template in self:
            template.x_free_qty = sum(template.product_variant_ids.mapped('free_qty'))

    @api.onchange('default_code')
    def onchange_internal_reference(self):
        for product in self:
            if product.default_code:
                internal_reference = product.default_code.upper()
                product.default_code = internal_reference
                product.description = internal_reference
                product.description_sale = internal_reference
                product.description_purchase = internal_reference
                product.description_picking = internal_reference
                product.description_pickingin = internal_reference
                product.description_pickingout = internal_reference

    def action_dummy(self):
        for product in self:
            pass


class ProductProduct(models.Model):
    _inherit = 'product.product'

    list_price = fields.Float(string="Sales LP")

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        sale_taxes = self.env['account.tax'].search([
            ('is_default_tax', '=', True),
            ('type_tax_use', '=', 'sale')
        ])
        purchase_taxes = self.env['account.tax'].search([
            ('is_default_tax', '=', True),
            ('type_tax_use', '=', 'purchase')
        ])

        if sale_taxes:
            res['taxes_id'] = [(6, 0, sale_taxes.ids)]
        if purchase_taxes:
            res['supplier_taxes_id'] = [(6, 0, purchase_taxes.ids)]

        res.update({
            'is_storable': True,
            'tracking': 'none',
            'invoice_policy': 'delivery',
            'purchase_method': 'receive'
        })

        return res

    @api.onchange('default_code')
    def onchange_internal_reference(self):
        for product in self:
            if product.default_code:
                internal_reference = product.default_code.upper()
                product.default_code = internal_reference
                product.description = internal_reference
                product.description_sale = internal_reference
                product.description_purchase = internal_reference
                product.description_picking = internal_reference
                product.description_pickingin = internal_reference
                product.description_pickingout = internal_reference

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


class ProductRemoval(models.Model):
    _inherit = 'product.removal'

    is_default = fields.Boolean(string="Is Default?")

    @api.constrains('is_default')
    def _check_is_default(self):
        for rec in self:
            if self.search_count([('is_default', '=', rec.is_default)]) > 1:
                raise ValidationError("Default removal strategy cannot be more than one!")