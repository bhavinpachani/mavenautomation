from odoo import models, fields


class IndiaMartEnquiry(models.Model):
    _name = 'indiamart.enquiry'
    _description = 'IndiaMart Enquiry Account'
    _rec_name = 'name'

    name = fields.Char('Name', required=True)
    mobile = fields.Char('Mobile', required=True)
    key = fields.Char('Key', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
    )
