from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    carrier_tracking_ref = fields.Char(string="Tracking Reference", copy=False)
    file = fields.Binary(string="Attachment")
    store_file = fields.Char(string="File Name")
    po_no_ref = fields.Selection(
        [('verbal', 'Verbal'), ('po', 'PO File')],
        tracking=1,
        string="Reference PO NO"
    )
    # payment_term_boolean = fields.Boolean(string="Payment Term Boolean")
    po_description = fields.Char(string="PO Description", tracking=1)
    advance_payment = fields.Float(string="Advance Payment")

    @api.constrains('po_no_ref', 'file', 'state')
    def _check_ir_attachment(self):
        params = self.env['ir.config_parameter'].sudo()
        validate_so_po = params.get_param('mavenautomation.validate_so_po') == 'True'
        for rec in self:
            if rec.state == 'sale':
                if validate_so_po and not rec.po_no_ref:
                    raise UserError(_("Enter PO Reference Number"))

                if rec.po_no_ref == 'po' and not rec.file:
                    raise UserError(_("Please upload document for this record"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            date_order = vals.get('date_order') or fields.Datetime.now()
            fy = self._get_fiscal_year(fields.Datetime.to_datetime(date_order))

            sequence_code = f"sale.order.{fy}"

            seq = self.env['ir.sequence'].next_by_code(sequence_code)

            if not seq:
                # create sequence dynamically if not exists
                self.env['ir.sequence'].create({
                    'name': f"Sale Order {fy}",
                    'code': sequence_code,
                    'prefix': f"SO/{fy}/",
                    'padding': 4,
                    'company_id': vals.get('company_id') or self.env.company.id,
                })
                seq = self.env['ir.sequence'].next_by_code(sequence_code)

            vals['name'] = seq

        return super().create(vals_list)

    def _get_fiscal_year(self, dt):
        if dt.month >= 4:
            return f"{str(dt.year)[-2:]}-{str(dt.year + 1)[-2:]}"
        return f"{str(dt.year - 1)[-2:]}-{str(dt.year)[-2:]}"

    def action_confirm(self):
        params = self.env['ir.config_parameter'].sudo()

        validate_so_vat = params.get_param('mavenautomation.validate_so_vat') == 'True'
        validate_so_email = params.get_param('mavenautomation.validate_so_email') == 'True'
        validate_so_mobile = params.get_param('mavenautomation.validate_so_mobile') == 'True'
        validate_so_payment_term = params.get_param('mavenautomation.validate_so_payment_term') == 'True'
        validate_so_salesman = params.get_param('mavenautomation.validate_so_salesman') == 'True'
        validate_so_address = params.get_param('mavenautomation.validate_so_address') == 'True'
        validate_so_delivery = params.get_param('mavenautomation.validate_so_delivery') == 'True'
        validate_so_industry_id = params.get_param('mavenautomation.validate_so_industry_id') == 'True'

        for order in self:
            missing_fields = []

            partner = order.partner_id

            if validate_so_vat and not partner.vat:
                missing_fields.append(_("VAT"))

            if validate_so_email and not partner.email:
                missing_fields.append(_("Email"))

            if validate_so_mobile and not partner.phone:
                missing_fields.append(_("Phone"))

            if validate_so_payment_term and not partner.property_payment_term_id:
                missing_fields.append(_("Customer Payment Term"))

            if validate_so_salesman and not partner.user_id:
                missing_fields.append(_("Salesman"))

            if validate_so_address:
                if not partner.street:
                    missing_fields.append(_("Address → Street"))
                if not partner.city:
                    missing_fields.append(_("Address → City"))
                if not partner.state_id:
                    missing_fields.append(_("Address → State"))

            if validate_so_delivery and not order.carrier_id:
                missing_fields.append(_("Delivery Method"))

            if validate_so_industry_id and not partner.industry_id:
                missing_fields.append(_("Contact Type"))

            if missing_fields:
                message = _(
                    "Customer information missing for %s:\n• %s"
                ) % (order.name, "\n• ".join(missing_fields))
                raise ValidationError(message)

        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    lead_time = fields.Char(string="Del. Time")
    price_unit = fields.Float(string="LP")
    unit_rate = fields.Float(
        string="Unit Rate",
        compute="_compute_unit_rate",
        store=True
    )
    price_subtotal = fields.Monetary(string="Subtotal")

    @api.depends('price_unit', 'product_uom_qty', 'discount')
    def _compute_unit_rate(self):
        for line in self:
            if line.product_uom_qty:
                total_after_discount = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0) / 100)
                line.unit_rate = total_after_discount / line.product_uom_qty
            else:
                line.unit_rate = line.price_unit