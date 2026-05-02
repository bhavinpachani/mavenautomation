from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _is_equal(self, a, b, precision):
        return abs(a - b) <= precision

    def action_post(self):
        for move in self:
            if move.move_type != 'in_invoice':
                continue

            for line in move.invoice_line_ids:
                po = line.purchase_order_id
                if not po:
                    continue

                # Match PO line
                po_line = po.order_line.filtered(
                    lambda l: l.product_id == line.product_id
                )

                if not po_line:
                    raise UserError(_(
                        "No matching Purchase Order line found for product: %s"
                    ) % line.product_id.display_name)

                # If multiple, take first (can improve later)
                po_line = po_line[0]

                precision = move.currency_id.rounding or 0.01

                # 🔴 Compare Quantity
                # if not self._is_equal(po_line.product_qty, line.quantity, precision):
                #     raise UserError(_(
                #         "Quantity mismatch!\n\n"
                #         "Product: %s\n"
                #         "PO Qty: %s\n"
                #         "Bill Qty: %s"
                #     ) % (
                #                         line.product_id.display_name,
                #                         po_line.product_qty,
                #                         line.quantity
                #                     ))

                # 🔴 Compare Subtotal (IMPORTANT)
                if not self._is_equal(po_line.price_subtotal, line.price_subtotal, precision):
                    raise UserError(_(
                        "Subtotal mismatch!\n\n"
                        "Product: %s\n"
                        "PO Subtotal: %s\n"
                        "Bill Subtotal: %s"
                    ) % (
                                        line.product_id.display_name,
                                        po_line.price_subtotal,
                                        line.price_subtotal
                                    ))

        return super().action_post()
