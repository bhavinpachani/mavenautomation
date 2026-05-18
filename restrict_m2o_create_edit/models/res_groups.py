# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    restrict_many2one_create_edit = fields.Boolean(
        string='Restrict Many2one Create/Edit',
        default=False,
        help="If enabled, users belonging to this group will not be able to "
             "Create, Create & Edit, Quick Create, or Open/Edit records from "
             "any Many2one field in the system.",
    )
