# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_standalone_delivery = fields.Boolean(
        string='Standalone Delivery',
        default=False,
        copy=False,
        tracking=True,
        index=True,
        help="Mark a delivery that was created directly, without a sales order. "
             "Done standalone deliveries can be selected on a customer invoice.",
    )
    inv_status = fields.Selection(
        selection=[
            ('pending', 'Pending'),
            ('invoiced', 'Invoiced'),
        ],
        string='Invoice Status',
        copy=False,
        index=True,
        help="Empty unless this is a standalone delivery. "
             "Pending until the delivery is selected on a customer invoice.",
    )
    standalone_invoice_ids = fields.Many2many(
        comodel_name='account.move',
        relation='account_move_standalone_picking_rel',
        column1='picking_id',
        column2='move_id',
        string='Standalone Invoices',
        copy=False,
    )

    @api.onchange('is_standalone_delivery', 'sale_id', 'picking_type_id')
    def _onchange_is_standalone_delivery(self):
        if self.state and self.state != 'draft':
            return
        if self.sale_id or self.picking_type_code != 'outgoing':
            self.is_standalone_delivery = False
        if self.is_standalone_delivery:
            if self.inv_status != 'invoiced':
                self.inv_status = 'pending'
        else:
            self.inv_status = False

    @api.constrains('is_standalone_delivery', 'sale_id', 'picking_type_code')
    def _check_is_standalone_delivery(self):
        for picking in self:
            if not picking.is_standalone_delivery:
                continue
            if picking.sale_id:
                raise ValidationError(_(
                    "Delivery %(delivery)s is linked to sales order %(order)s and cannot be a standalone delivery.",
                    delivery=picking.display_name,
                    order=picking.sale_id.display_name,
                ))
            if picking.picking_type_code != 'outgoing':
                raise ValidationError(_(
                    "Only delivery orders can be marked as standalone deliveries (%(delivery)s).",
                    delivery=picking.display_name,
                ))

    def _sync_inv_status_from_invoices(self):
        """Pending or Invoiced only for standalone deliveries. Otherwise empty."""
        grouped = {
            'invoiced': self.env['stock.picking'],
            'pending': self.env['stock.picking'],
            False: self.env['stock.picking'],
        }
        for picking in self:
            if not picking.is_standalone_delivery:
                target = False
            elif picking.standalone_invoice_ids.filtered(lambda inv: inv.state != 'cancel'):
                target = 'invoiced'
            else:
                target = 'pending'
            if picking.inv_status != target:
                grouped[target] |= picking
        for status, pickings in grouped.items():
            if pickings:
                pickings.with_context(sync_standalone_inv_status=True).sudo().write({
                    'inv_status': status,
                })

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get('sync_standalone_inv_status'):
            cleaned = []
            for vals in vals_list:
                vals = dict(vals)
                vals.pop('inv_status', None)
                vals['inv_status'] = 'pending' if vals.get('is_standalone_delivery') else False
                cleaned.append(vals)
            vals_list = cleaned
        return super().create(vals_list)

    def write(self, vals):
        vals = dict(vals)
        syncing = self.env.context.get('sync_standalone_inv_status')
        if 'inv_status' in vals and not syncing:
            vals.pop('inv_status')
            if not vals:
                return True
        if not syncing and 'is_standalone_delivery' in vals:
            new_value = bool(vals['is_standalone_delivery'])
            changing = self.filtered(lambda picking: bool(picking.is_standalone_delivery) != new_value)
            not_draft = changing.filtered(lambda picking: picking.state != 'draft')
            if not_draft:
                raise UserError(_(
                    "Standalone Delivery can only be changed while the delivery is in draft."
                ))
            if not new_value:
                linked = changing.filtered(
                    lambda picking: picking.standalone_invoice_ids.filtered(lambda inv: inv.state != 'cancel')
                )
                if linked:
                    raise UserError(_(
                        "Remove %(deliveries)s from the invoice before turning off Standalone Delivery.",
                        deliveries=", ".join(linked.mapped('display_name')),
                    ))
        res = super().write(vals)
        if not syncing and 'is_standalone_delivery' in vals:
            self._sync_inv_status_from_invoices()
        return res

    def action_cancel(self):
        invoiced = self.filtered(
            lambda picking: picking.standalone_invoice_ids.filtered(lambda inv: inv.state != 'cancel')
        )
        if invoiced:
            raise UserError(_(
                "Remove %(deliveries)s from the invoice before cancelling.",
                deliveries=", ".join(invoiced.mapped('display_name')),
            ))
        return super().action_cancel()
