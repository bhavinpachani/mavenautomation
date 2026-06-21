from odoo import models, api, _
from odoo.exceptions import ValidationError
from markupsafe import Markup

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.constrains('product_tmpl_id')
    def _check_unique_bom_per_product(self):
        for bom in self:
            domain = [
                ('product_tmpl_id', '=', bom.product_tmpl_id.id),
                ('id', '!=', bom.id),
            ]
            if self.search_count(domain):
                raise ValidationError(
                    _("Only one BoM is allowed per product: %s") % bom.product_tmpl_id.display_name
                )

    def write(self, vals):
        if 'bom_line_ids' in vals:
            # Capture old state of BOM lines before write
            old_lines_data = {}
            for bom in self:
                old_lines_data[bom.id] = {
                    line.id: {
                        'product_id': line.product_id,
                        'product_qty': line.product_qty,
                        'product_uom_id': line.product_uom_id,
                    }
                    for line in bom.bom_line_ids
                }

        res = super().write(vals)

        if 'bom_line_ids' in vals:
            for bom in self:
                old_data = old_lines_data.get(bom.id, {})
                new_lines = bom.bom_line_ids

                old_line_ids = set(old_data.keys())
                new_line_ids = set(new_lines.ids)

                added_ids = new_line_ids - old_line_ids
                removed_ids = old_line_ids - new_line_ids
                common_ids = old_line_ids & new_line_ids

                log_parts = []

                # --- Added lines ---
                if added_ids:
                    added_lines = new_lines.filtered(lambda l: l.id in added_ids)
                    rows = ""
                    for line in added_lines:
                        rows += (
                            "<tr>"
                            "<td style='padding:4px 8px;'>%s</td>"
                            "<td style='padding:4px 8px;'>%s</td>"
                            "<td style='padding:4px 8px;'>%s</td>"
                            "</tr>"
                        ) % (
                            line.product_id.display_name,
                            line.product_qty,
                            line.product_uom_id.name,
                        )
                    log_parts.append(
                        "<b>&#x2795; BoM Line(s) Added:</b>"
                        "<table style='border-collapse:collapse; margin:4px 0;'>"
                        "<tr style='background:#e8f5e9;'>"
                        "<th style='padding:4px 8px; text-align:left;'>Product</th>"
                        "<th style='padding:4px 8px; text-align:left;'>Quantity</th>"
                        "<th style='padding:4px 8px; text-align:left;'>UoM</th>"
                        "</tr>"
                        "%s"
                        "</table>" % rows
                    )

                # --- Removed lines ---
                if removed_ids:
                    rows = ""
                    for line_id in removed_ids:
                        data = old_data[line_id]
                        rows += (
                            "<tr>"
                            "<td style='padding:4px 8px;'>%s</td>"
                            "<td style='padding:4px 8px;'>%s</td>"
                            "<td style='padding:4px 8px;'>%s</td>"
                            "</tr>"
                        ) % (
                            data['product_id'].display_name,
                            data['product_qty'],
                            data['product_uom_id'].name,
                        )
                    log_parts.append(
                        "<b>&#x274C; BoM Line(s) Removed:</b>"
                        "<table style='border-collapse:collapse; margin:4px 0;'>"
                        "<tr style='background:#ffebee;'>"
                        "<th style='padding:4px 8px; text-align:left;'>Product</th>"
                        "<th style='padding:4px 8px; text-align:left;'>Quantity</th>"
                        "<th style='padding:4px 8px; text-align:left;'>UoM</th>"
                        "</tr>"
                        "%s"
                        "</table>" % rows
                    )

                # --- Modified lines ---
                modified_rows = ""
                for line_id in common_ids:
                    old = old_data[line_id]
                    new_line = new_lines.filtered(lambda l: l.id == line_id)
                    if not new_line:
                        continue
                    new_line = new_line[0]
                    changes = []
                    if old['product_id'] != new_line.product_id:
                        changes.append(
                            "Product: %s &#x2192; %s" % (
                                old['product_id'].display_name,
                                new_line.product_id.display_name,
                            )
                        )
                    if old['product_qty'] != new_line.product_qty:
                        changes.append(
                            "Quantity: %s &#x2192; %s" % (
                                old['product_qty'],
                                new_line.product_qty,
                            )
                        )
                    if old['product_uom_id'] != new_line.product_uom_id:
                        changes.append(
                            "UoM: %s &#x2192; %s" % (
                                old['product_uom_id'].name,
                                new_line.product_uom_id.name,
                            )
                        )
                    if changes:
                        modified_rows += (
                            "<tr><td style='padding:4px 8px;'>%s</td>"
                            "<td style='padding:4px 8px;'>%s</td></tr>"
                        ) % (
                            new_line.product_id.display_name,
                            "<br/>".join(changes),
                        )

                if modified_rows:
                    log_parts.append(
                        "<b>&#x270F; BoM Line(s) Modified:</b>"
                        "<table style='border-collapse:collapse; margin:4px 0;'>"
                        "<tr style='background:#fff3e0;'>"
                        "<th style='padding:4px 8px; text-align:left;'>Product</th>"
                        "<th style='padding:4px 8px; text-align:left;'>Changes</th>"
                        "</tr>"
                        "%s"
                        "</table>" % modified_rows
                    )

                if log_parts:
                    body = Markup("<br/>".join(log_parts))
                    bom.message_post(body=body, subtype_xmlid='mail.mt_note')

        return res