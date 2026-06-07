# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class ResPartner(models.Model):
    _inherit = 'res.partner'

    contact_name = fields.Char(string="Contact Name")
    is_email_none = fields.Boolean(string="E.None")
    is_phone_none = fields.Boolean(string="M.None")

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name)]) > 1:
                raise ValidationError("Name must be unique!")

    @api.model
    def default_get(self, fields):
        res = super(ResPartner, self).default_get(fields)
        if res:
            res.update({
                'l10n_in_gst_treatment': 'regular'
            })
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name'):
                vals['name'] = vals['name'].upper()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('name'):
            vals['name'] = vals['name'].upper()
        return super().write(vals)

    @api.constrains('email', 'phone', 'is_email_none', 'is_phone_none')
    def _check_email_or_phone(self):
        """Ensure at least one of email or phone is provided and valid, and only one can be 'N/A'."""
        email_regex = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$'
        phone_regex = r'^\d{10}$'  # Exactly 10 digits

        for rec in self:
            email_val = rec.email if not rec.is_email_none else False
            phone_val = rec.phone if not rec.is_phone_none else False

            # At least one must exist and not both be False or "N/A"
            if (not email_val or email_val == "N/A") and (not phone_val or phone_val == "N/A"):
                raise ValidationError("You must provide at least one valid Email or Phone number.")

            # Check if both are "N/A"
            if email_val == "N/A" and phone_val == "N/A":
                raise ValidationError("Only one of Email or Phone can be 'N/A', not both.")

            # Validate email
            if email_val and email_val != "N/A":
                if not re.match(email_regex, email_val.lower()):
                    raise ValidationError(f"Invalid Email format: {email_val}")

            # Validate phone
            if phone_val and phone_val != "N/A":
                if not re.match(phone_regex, phone_val):
                    raise ValidationError(f"Invalid Phone number: {phone_val}. Must be 10 digits.")

    # Automatically set "N/A" if the boolean flags are checked
    @api.onchange('is_email_none', 'is_phone_none')
    def _onchange_set_na(self):
        for rec in self:
            if rec.is_email_none:
                rec.email = "N/A"

            if rec.is_phone_none:
                rec.phone = "N/A"