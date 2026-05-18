# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
from odoo.http import request

_RESTRICT_GROUP = 'restrict_m2o_create_edit.group_restrict_m2o_create_edit'


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        """Pass the M2O restriction flag to the frontend via session_info."""
        res = super().session_info()
        if request.session.uid:
            res['restrict_many2one_create_edit'] = (
                self.env.user._is_m2o_create_edit_restricted()
            )
        return res

    def get_frontend_session_info(self):
        """Also cover website/portal contexts."""
        res = super().get_frontend_session_info()
        if request.session.uid:
            res['restrict_many2one_create_edit'] = (
                self.env.user._is_m2o_create_edit_restricted()
            )
        return res
