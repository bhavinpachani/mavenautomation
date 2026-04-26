from odoo import models, fields
from odoo.tools.sql import SQL

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    purchase_for_id = fields.Many2one(
        'purchase.for',
        string='Purchase For',
        readonly=True
    )

    def _select(self):
        return SQL(
            "%s, l.purchase_for_id AS purchase_for_id",
            super()._select()
        )

    def _group_by(self):
        return SQL(
            "%s, l.purchase_for_id",
            super()._group_by()
        )