# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError



class AccountMove(models.Model):
    _inherit = 'account.move'

    round_off_value = fields.Monetary(
        string='Round off amount',
        store=True,
        readonly=True,
        compute='_compute_roundoff_amounts',
    )
    round_off_amount = fields.Float(string='Round off Amount')
    rounded_total = fields.Monetary(
        string='Rounded Total',
        store=True,
        readonly=True,
        compute='_compute_roundoff_amounts',
    )
    round_active = fields.Boolean(
        'Enabled Roundoff',
        default=lambda self: self.env['ir.config_parameter'].sudo().get_param(
            'account.invoice_roundoff'
        ),
    )

    @api.depends('amount_total', 'round_active')
    def _compute_roundoff_amounts(self):
        """
        Compute round-off fields from the already-computed amount_total.
        This runs AFTER Odoo's _compute_amount so amount_total is finalised.
        """
        for move in self:
            if move.round_active and move.amount_total:
                amount_total_rounded = round(move.amount_total)
                round_off = amount_total_rounded - move.amount_total
                move.round_off_value = round_off
                move.round_off_amount = round_off
                move.rounded_total = amount_total_rounded
            else:
                move.round_off_value = 0.0
                move.round_off_amount = 0.0
                move.rounded_total = 0.0

    def _construct_values(self, account_id, amount):
        return (0, 0, {
            'name': 'Roundoff Amount',
            'account_id': account_id,
            'quantity': 1.0,
            'price_unit': amount,
            'is_roundoff_line': True,
        })

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE — inject roundoff lines when creating invoices from SO/PO
        for vals in vals_list:
            if 'invoice_line_ids' not in vals:
                continue

            account_id_raw = self.env['ir.config_parameter'].sudo().get_param(
                'account.roundoff_account_id'
            )
            if not account_id_raw:
                continue
            account_id = int(account_id_raw)

            if (
                self.env.context.get('active_model') == 'sale.order'
                and self.env.context.get('active_id')
            ):
                sale = self.env['sale.order'].browse(self.env.context['active_id'])
                if sale and sale.is_enabled_roundoff and sale.amount_round_off:
                    values = self._construct_values(account_id, sale.amount_round_off)
                    vals['invoice_line_ids'].append(values)

            # Vendor Bills from Purchase Orders
            # PO's action_create_invoice doesn't pass active_model in context,
            # so we match via invoice_origin which holds the PO name.
            elif vals.get('move_type') == 'in_invoice' and vals.get('invoice_origin'):
                po_names = [n.strip() for n in vals['invoice_origin'].split(',')]
                purchases = self.env['purchase.order'].search([
                    ('name', 'in', po_names),
                    ('is_enabled_roundoff', '=', True),
                ])
                if purchases:
                    total_round_off = sum(purchases.mapped('amount_round_off'))
                    if total_round_off:
                        values = self._construct_values(account_id, total_round_off)
                        vals['invoice_line_ids'].append(values)

            elif vals.get('round_active') and vals.get('round_off_amount'):
                # Direct creation with roundoff (e.g. from PO)
                round_off_amount = vals['round_off_amount']
                flag = False
                for record in vals.get('line_ids', []):
                    if not (isinstance(record, (list, tuple)) and len(record) == 3):
                        continue
                    line_vals = record[2]
                    if not line_vals.get('account_id'):
                        continue
                    account = self.env['account.account'].browse(line_vals['account_id'])
                    # Update receivable line for sale-type invoices
                    if account.account_type == 'asset_receivable':
                        adj = abs(line_vals.get('price_unit', 0.0))
                        if round_off_amount < 0.0:
                            total = adj - abs(round_off_amount)
                        else:
                            total = adj + abs(round_off_amount)
                        line_vals['price_unit'] = -total
                        line_vals['debit'] = total
                        flag = True
                    # Update payable line for purchase-type invoices
                    elif account.account_type == 'liability_payable':
                        adj = abs(line_vals.get('price_unit', 0.0))
                        if round_off_amount < 0.0:
                            total = adj - abs(round_off_amount)
                        else:
                            total = adj + abs(round_off_amount)
                        line_vals['price_unit'] = -total
                        line_vals['credit'] = total
                        flag = True

                if flag:
                    values = self._construct_values(account_id, round_off_amount)
                    vals.setdefault('line_ids', []).append(values)
                    vals['invoice_line_ids'].append(values)

        return super(AccountMove, self).create(vals_list)



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_roundoff_line = fields.Boolean('Roundoff Line', default=False)