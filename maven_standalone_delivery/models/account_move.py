# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, Command
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    standalone_picking_ids = fields.Many2many(
        comodel_name='stock.picking',
        relation='account_move_standalone_picking_rel',
        column1='move_id',
        column2='picking_id',
        string='Deliveries',
        copy=False,
        domain="""[
            '|',
                ('id', 'in', standalone_picking_ids),
                '&', '&', '&', '&', '&', '&',
                    ('is_standalone_delivery', '=', True),
                    ('state', '=', 'done'),
                    ('picking_type_code', '=', 'outgoing'),
                    ('inv_status', '=', 'pending'),
                    ('partner_id', '!=', False),
                    ('partner_id.commercial_partner_id', '=', commercial_partner_id),
                    '|',
                        ('company_id', '=', False),
                        ('company_id', '=', company_id)
        ]""",
        help="Done standalone deliveries for this customer. "
             "Deliveries linked to a sales order are not listed.",
    )

    @api.onchange('partner_id', 'move_type', 'invoice_line_ids')
    def _onchange_standalone_pickings(self):
        pickings = self.standalone_picking_ids
        if not pickings:
            return
        if (
            self.move_type != 'out_invoice'
            or not self.partner_id
            or self.invoice_line_ids.sale_line_ids
        ):
            self.standalone_picking_ids = [Command.clear()]
            return
        commercial = self.partner_id.commercial_partner_id
        kept = pickings.filtered(
            lambda picking: picking.partner_id.commercial_partner_id == commercial
        )
        if kept != pickings:
            self.standalone_picking_ids = kept

    def _standalone_picking_error(self, picking):
        self.ensure_one()
        if picking.picking_type_code != 'outgoing' or picking.sale_id or not picking.is_standalone_delivery:
            return _(
                "%(delivery)s is not a standalone delivery order.",
                delivery=picking.display_name,
            )
        if picking.state != 'done':
            return _(
                "%(delivery)s must be done before it can be added to an invoice.",
                delivery=picking.display_name,
            )
        if (
            not self.partner_id
            or not picking.partner_id
            or picking.partner_id.commercial_partner_id != self.commercial_partner_id
        ):
            return _(
                "%(delivery)s does not belong to this customer.",
                delivery=picking.display_name,
            )
        if picking.company_id and self.company_id and picking.company_id != self.company_id:
            return _(
                "%(delivery)s belongs to another company.",
                delivery=picking.display_name,
            )
        other_invoices = picking.standalone_invoice_ids.filtered(
            lambda invoice: invoice != self and invoice.state != 'cancel'
        )
        if other_invoices:
            return _(
                "%(delivery)s is already selected on %(invoice)s.",
                delivery=picking.display_name,
                invoice=", ".join(other_invoices.mapped('display_name')),
            )
        return False

    @api.constrains(
        'standalone_picking_ids', 'partner_id', 'move_type', 'company_id', 'state', 'line_ids',
    )
    def _check_standalone_pickings(self):
        for move in self:
            pickings = move.standalone_picking_ids
            if not pickings:
                continue
            if move.state == 'cancel':
                raise ValidationError(_("Deliveries cannot be kept on a cancelled invoice."))
            if move.move_type != 'out_invoice':
                raise ValidationError(_("Deliveries can only be set on customer invoices."))
            if move.line_ids.sale_line_ids:
                raise ValidationError(_(
                    "Deliveries can only be set on invoices that are not linked to a sales order."
                ))
            if not move.partner_id:
                raise ValidationError(_("Select a customer before choosing deliveries."))
            errors = [error for error in (move._standalone_picking_error(picking) for picking in pickings) if error]
            if errors:
                raise ValidationError("\n".join(errors))

    def _sync_standalone_picking_status(self, previous_pickings):
        current = self.standalone_picking_ids
        (previous_pickings | current)._sync_inv_status_from_invoices()

    @api.model_create_multi
    def create(self, vals_list):
        moves = super().create(vals_list)
        moves.filtered('standalone_picking_ids').standalone_picking_ids._sync_inv_status_from_invoices()
        return moves

    def write(self, vals):
        previous = self.standalone_picking_ids if 'standalone_picking_ids' in vals else self.env['stock.picking']
        res = super().write(vals)
        if 'standalone_picking_ids' in vals:
            self._sync_standalone_picking_status(previous)
        return res

    def unlink(self):
        pickings = self.standalone_picking_ids
        res = super().unlink()
        if pickings:
            pickings._sync_inv_status_from_invoices()
        return res

    def button_cancel(self):
        moves = self.filtered('standalone_picking_ids')
        if moves:
            moves.write({'standalone_picking_ids': [Command.clear()]})
        return super().button_cancel()
