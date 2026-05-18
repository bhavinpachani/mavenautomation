# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.exceptions import AccessError

_RESTRICT_GROUP = 'restrict_m2o_create_edit.group_restrict_m2o_create_edit'


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def name_create(self, name):
        """Block quick-creation via RPC when the user is in the restriction group.

        This is the backend guard — prevents bypassing the JS restriction by
        calling the endpoint directly.
        """
        if self.env.user._is_m2o_create_edit_restricted():
            raise AccessError(
                self.env._(
                    "You are not allowed to create records from Many2one fields. "
                    "Contact your administrator if you need this access."
                )
            )
        return super().name_create(name)


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _is_m2o_create_edit_restricted(self):
        """Return True if this user is subject to the M2O create/edit restriction.

        Superusers are always exempt.
        """
        self.ensure_one()
        if self._is_superuser():
            return False
        return self.has_group(_RESTRICT_GROUP)
