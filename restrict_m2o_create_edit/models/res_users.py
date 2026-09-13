from odoo import models, api

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)

        group = self.env.ref(
            "restrict_m2o_create_edit.group_restrict_m2o_create_edit"
        )

        users.sudo().write({
            "group_ids": [(4, group.id)]
        })

        return users

    def write(self, vals):
        res = super().write(vals)

        if "groups_id" in vals:
            self.env.registry.clear_cache("templates")

        return res