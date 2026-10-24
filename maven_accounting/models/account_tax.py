# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain
import re


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_default_tax = fields.Boolean(string="Default Tax")
    is_searchable = fields.Boolean(string="Searchable", default=False)

    @api.onchange('is_default_tax', 'is_searchable')
    def _onchange_default_tax_searchable(self):
        if self.is_default_tax:
            self.is_searchable = True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('is_default_tax'):
                vals['is_searchable'] = True
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('is_default_tax'):
            vals = dict(vals, is_searchable=True)
            return super().write(vals)
        if vals.get('is_searchable') is False and 'is_default_tax' not in vals:
            default_taxes = self.filtered('is_default_tax')
            other_taxes = self - default_taxes
            if default_taxes and other_taxes:
                return super(AccountTax, other_taxes).write(vals)
            if default_taxes:
                return True
        return super().write(vals)

    @api.model
    def name_search(self, name='', domain=None, operator='ilike', limit=100):
        # Order-line tax dropdowns call name_search with their own domain.
        domain = self._searchable_domain(domain)
        return super().name_search(name, domain, operator, limit)

    @api.model
    def _searchable_domain(self, domain):
        domain = Domain(domain or Domain.TRUE)
        if (
            self.env.context.get('searchable_test', True)
            and not any(
                condition.field_expr == 'is_searchable'
                for condition in domain.iter_conditions()
            )
        ):
            domain &= Domain('is_searchable', '=', True)
        return domain

    @api.model
    def _search(self, domain, offset=0, limit=None, order=None, active_test=True, bypass_access=False):
        """Hide non-searchable taxes from dropdowns, but never from reads of a known tax.

        ``_fetch`` loads records with ``active_test=False`` and an id domain. Folding
        ``is_searchable`` into that query drops the tax and Odoo reports it as an
        access error, with no record rule to blame.
        """
        if self._apply_searchable_filter(domain, active_test=active_test, bypass_access=bypass_access):
            domain = self._searchable_domain(domain)
        return super()._search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            active_test=active_test,
            bypass_access=bypass_access,
        )

    @api.model
    def _apply_searchable_filter(self, domain, active_test=True, bypass_access=False):
        if self.env.su or bypass_access or not active_test:
            return False
        try:
            return not any(
                condition.field_expr == 'id'
                for condition in Domain(domain or Domain.TRUE).iter_conditions()
            )
        except Exception:
            return True

    def init(self):
        # New boolean columns are NULL, which does not match "is_searchable = True".
        # Default taxes are always searchable.
        self.env.cr.execute("""
            UPDATE account_tax
               SET is_searchable = TRUE
             WHERE is_searchable IS NULL
                OR is_default_tax IS TRUE
        """)