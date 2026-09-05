
from odoo import models,api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if self.env.user.has_group('maven_access_rights.group_contact_read_only_access'):
            if view_type == 'form':
                for node in arch.xpath("//form"):
                    node.set("create", '0')
                    node.set("edit", '0')
                    node.set("delete", '0')
            if view_type == 'list':
                for node in arch.xpath("//list"):
                    node.set("create", '0')
                    node.set("edit", '0')
                    node.set("delete", '0')
        return arch, view
