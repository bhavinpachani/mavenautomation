from odoo import models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    bom_updated = fields.Boolean(default=False, copy=False)

    def do_unreserve(self):
        for production in self:

            raw_moves = production.move_raw_ids.filtered(
                lambda m: m.state not in ('done', 'cancel')
            )

            for move in raw_moves:

                # Clear consumed qty
                for line in move.move_line_ids:
                    line.quantity = 0

                # Unreserve
                move._do_unreserve()

                # Recompute
                move._recompute_state()

        return True

    def action_update_bom(self):
        for mo in self:
            if not mo.bom_id:
                raise UserError(_("No BoM found on this Manufacturing Order."))

            bom = mo.bom_id

            # Store old BoM lines
            old_lines = {
                line.product_id.id: line.product_qty
                for line in bom.bom_line_ids
            }

            # Collect MO components
            new_lines = {}
            for move in mo.move_raw_ids:
                if move.quantity > 0:
                    new_lines[move.product_id.id] = move.quantity

            if not new_lines:
                raise UserError(_("No components with quantity > 0 found."))

            # Prepare change log
            log_lines = []

            # Added / Updated
            for product_id, qty in new_lines.items():
                product = self.env['product.product'].browse(product_id)

                if product_id not in old_lines:
                    log_lines.append(
                        f"<li>Added: <b>{product.display_name}</b> (Qty: {qty})</li>"
                    )
                elif old_lines[product_id] != qty:
                    log_lines.append(
                        f"<li>Updated: <b>{product.display_name}</b> "
                        f"({old_lines[product_id]} → {qty})</li>"
                    )

            # Removed
            for product_id, qty in old_lines.items():
                if product_id not in new_lines:
                    product = self.env['product.product'].browse(product_id)
                    log_lines.append(
                        f"<li>Removed: <b>{product.display_name}</b> "
                        f"(Old Qty: {qty})</li>"
                    )

            # Replace BoM lines
            bom.bom_line_ids.unlink()

            bom.write({
                'bom_line_ids': [
                    (0, 0, {
                        'product_id': product_id,
                        'product_qty': qty,
                        'product_uom_id': self.env['product.product'].browse(product_id).uom_id.id,
                    })
                    for product_id, qty in new_lines.items()
                ]
            })

            # Post chatter message on BoM
            if log_lines:
                bom.message_post(
                    body=Markup(
                        f"<p><b>BoM updated from Manufacturing Order {mo.name}</b></p>"
                        f"<ul>{''.join(log_lines)}</ul>"
                    )
                )

            mo.bom_updated = True

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('BoM updated successfully from Manufacturing Order components.'),
                'type': 'success',
            }
        }