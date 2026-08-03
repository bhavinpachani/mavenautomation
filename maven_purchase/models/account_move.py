from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _is_equal(self, a, b, precision):
        return abs(a - b) <= precision

#    def action_post(self):
#        for move in self:
#            if move.move_type != 'in_invoice':
#                continue

#            for line in move.invoice_line_ids:
#                po = line.purchase_order_id
#                if not po:
#                    continue

                # Match PO line by product
#                po_line = po.order_line.filtered(
#                    lambda l: l.product_id == line.product_id
#                )

#                if not po_line:
#                    raise UserError(_(
#                        "No matching Purchase Order line found for product: %s"
#                    ) % line.product_id.display_name)

                # Take first match
#                po_line = po_line[0]
#
#                precision = move.currency_id.rounding or 0.01

                # 🔴 Compare Unit Rate only
#                if not self._is_equal(po_line.unit_rate, line.price_unit, precision):
#                    raise UserError(_(
#                        "Unit Rate mismatch!\n\n"
#                        "Product: %s\n"
#                        "PO Unit Rate: %s\n"
#                        "Bill Unit Rate: %s"
#                    ) % (
#                                        line.product_id.display_name,
#                                        po_line.unit_rate,
#                                        line.price_unit
#                                    ))

#        return super().action_post()

