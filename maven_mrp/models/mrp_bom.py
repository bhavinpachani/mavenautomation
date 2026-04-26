from odoo import models, api, _
from odoo.exceptions import ValidationError

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