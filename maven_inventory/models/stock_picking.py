# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.model
    def _default_responsible_user(self):
        # Delivery Orders are created directly. Do not prefill the current user.
        if self.env.context.get('restricted_picking_type_code') == 'outgoing':
            return False
        return self.env.user

    user_id = fields.Many2one(default=_default_responsible_user)
    challan_type_id = fields.Many2one(
        'inventory.challan.type',
        string='Challan Type',
        copy=False,
        tracking=True,
        ondelete='restrict',
    )
