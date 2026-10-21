# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    tax_ids = fields.Many2many(
        domain="[('type_tax_use', '=', 'purchase'), ('is_searchable', '=', True)]",
    )

    def _compute_tax_id(self):
        super()._compute_tax_id()
        for line in self:
            line.tax_ids = line.tax_ids.filtered('is_searchable')

    def _prepare_purchase_order_line(self, product_id, product_qty, product_uom, company_id, partner_id, po):
        values = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, partner_id, po,
        )
        tax_commands = values.get('tax_ids') or []
        for command in tax_commands:
            if command and command[0] == 6:
                searchable_ids = self.env['account.tax'].browse(command[2]).filtered('is_searchable').ids
                values['tax_ids'] = [(6, 0, searchable_ids)]
                break
        return values
