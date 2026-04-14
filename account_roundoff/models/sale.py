from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_enabled_roundoff = fields.Boolean(
        string="Enable Round Off"
    )

    amount_round_off = fields.Monetary(
        string='Round Off Amount',
        compute='_compute_roundoff',
        store=True
    )

    amount_round_off_total = fields.Monetary(
        string='Rounded Total',
        compute='_compute_roundoff',
        store=True
    )

    @api.depends('amount_total', 'is_enabled_roundoff')
    def _compute_roundoff(self):
        params = self.env['ir.config_parameter'].sudo()
        is_enabled_roundoff = params.get_param('account.invoice_roundoff')
        for order in self:
            if is_enabled_roundoff and order.amount_total:
                rounded_total = round(order.amount_total)
                round_off = rounded_total - order.amount_total

                order.amount_round_off_total = rounded_total
                order.amount_round_off = round_off
            else:
                order.amount_round_off_total = 0.0
                order.amount_round_off = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        roundoff_enabled = self.env['ir.config_parameter'].sudo().get_param(
            'account.invoice_roundoff'
        ) == 'True'

        for vals in vals_list:
            vals['is_enabled_roundoff'] = roundoff_enabled

        return super(SaleOrder, self).create(vals_list)