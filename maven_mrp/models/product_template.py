from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    mrp_ok = fields.Boolean(default=False)

    def _get_fiscal_year(self, dt):
        if dt.month >= 4:
            return f"{str(dt.year)[-2:]}-{str(dt.year + 1)[-2:]}"
        return f"{str(dt.year - 1)[-2:]}-{str(dt.year)[-2:]}"

    def _get_or_create_sequence(self, fy):
        sequence_code = f"product.template.{fy}"
        seq = self.env['ir.sequence'].next_by_code(sequence_code)
        if not seq:
            self.env['ir.sequence'].sudo().create({
                'name': f"Panel Product {fy}",
                'code': sequence_code,
                'prefix': f"WO/{fy}/",
                'padding': 4,
                'company_id': self.env.company.id,
            })
            seq = self.env['ir.sequence'].next_by_code(sequence_code)
        return seq

    @api.model
    def default_get(self, fields_list):
        """Pre-fill name with a draft placeholder so form can open."""
        res = super().default_get(fields_list)
        is_mrp = self.env.context.get('default_mrp_ok', False)
        if is_mrp and 'name' in fields_list:
            res['name'] = 'New'   # placeholder — replaced on actual save
            res['mrp_ok'] = True
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            is_mrp = vals.get('mrp_ok', self.env.context.get('default_mrp_ok', False))
            if is_mrp:
                create_date = fields.Datetime.now()
                fy = self._get_fiscal_year(create_date)
                seq = self._get_or_create_sequence(fy)
                vals['name'] = seq
                vals['mrp_ok'] = True
        return super().create(vals_list)