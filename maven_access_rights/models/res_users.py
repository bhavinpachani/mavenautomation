from odoo import models

class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        res = super().write(vals)

        if "groups_id" in vals:
            self.env.registry.clear_cache("templates")

        return res