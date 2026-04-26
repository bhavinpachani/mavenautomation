from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = "mrp.production"

    bom_updated = fields.Boolean(default=False)

    def action_update_bom(self):
        for mo in self:
            if not mo.bom_id:
                raise UserError("No BoM found on this Manufacturing Order.")

            bom = mo.bom_id

            # Collect components from MO (only qty > 0)
            lines_to_keep = []
            for move in mo.move_raw_ids:
                qty = move.product_uom_qty
                if qty > 0:
                    lines_to_keep.append((move.product_id, qty))

            if not lines_to_keep:
                raise UserError("No components with quantity > 0 found.")

            # Remove existing BoM lines
            bom.bom_line_ids.unlink()

            # Create new BoM lines
            bom_lines = []
            for product, qty in lines_to_keep:
                bom_lines.append((0, 0, {
                    'product_id': product.id,
                    'product_qty': qty,
                    'product_uom_id': product.uom_id.id,
                }))

            bom.write({'bom_line_ids': bom_lines})
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