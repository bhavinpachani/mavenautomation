from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    show_discount = fields.Boolean(string="Show Discount")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            date_order = vals.get('date_order') or fields.Datetime.now()
            fy = self._get_fiscal_year(fields.Datetime.to_datetime(date_order))

            sequence_code = f"purchase.order.{fy}"

            seq = self.env['ir.sequence'].next_by_code(sequence_code)

            if not seq:
                self.env['ir.sequence'].create({
                    'name': f"Purchase Order {fy}",
                    'code': sequence_code,
                    'prefix': f"PO/{fy}/",
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

    def get_merged_report_lines(self):
        self.ensure_one()
        merged_lines = self.env['purchase.order.line'].browse()
        seen_products = {}

        for line in self.order_line:
            if line.display_type or not line.product_id:
                merged_lines += line
                continue

            product_id = line.product_id.id
            if product_id in seen_products:
                seen_line = seen_products[product_id]
                seen_line.update({
                    'product_qty': seen_line.product_qty + line.product_qty,
                    'price_subtotal': seen_line.price_subtotal + line.price_subtotal,
                })
            else:
                new_line = self.env['purchase.order.line'].new({
                    'order_id': self.id,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_qty': line.product_qty,
                    'price_unit': line.price_unit,
                    'date_planned': line.date_planned,
                    'discount': line.discount,
                    'unit_rate': line.unit_rate,
                    'price_subtotal': line.price_subtotal,
                    'display_type': line.display_type,
                    'tax_ids': [(6, 0, line.tax_ids.ids)],
                    'product_uom_id': line.product_uom.id,
                })
                seen_products[product_id] = new_line
                merged_lines += new_line

        return merged_lines

    def button_confirm(self):
        params = self.env['ir.config_parameter'].sudo()

        def get_bool(param):
            return params.get_param(param) == 'True'

        validate_po_vat = get_bool('mavenautomation.validate_po_vat')
        validate_po_email = get_bool('mavenautomation.validate_po_email')
        validate_po_mobile = get_bool('mavenautomation.validate_po_mobile')
        validate_po_payment_term = get_bool('mavenautomation.validate_po_payment_term')
        validate_po_address = get_bool('mavenautomation.validate_po_address')
        validate_po_tag = get_bool('mavenautomation.validate_po_tag')
        validate_po_industry_id = get_bool('mavenautomation.validate_po_industry_id')

        for order in self:
            partner = order.partner_id.parent_id or order.partner_id
            validate_msgs = []

            # VAT
            if validate_po_vat and not partner.vat:
                validate_msgs.append("Vat")

            # Email
            if validate_po_email and not partner.email:
                validate_msgs.append("Email")

            # Mobile
            if validate_po_mobile and not partner.phone:
                validate_msgs.append("Phone")

            # Payment Term
            if validate_po_payment_term and not partner.property_supplier_payment_term_id:
                validate_msgs.append("Vendor Payment Term")

            # Address
            if validate_po_address:
                if not partner.street:
                    validate_msgs.append("Address -> Street")
                if not partner.city:
                    validate_msgs.append("Address -> City")
                if not partner.state_id:
                    validate_msgs.append("Address -> State")

            # Tags
            if validate_po_tag and not partner.category_id:
                validate_msgs.append("Deal In")

            # Industry
            if validate_po_industry_id and not partner.industry_id:
                validate_msgs.append("Contact Type")

            if validate_msgs:
                msg = "Vendor Information Missing for %s\n\t*\t" % order.name
                msg += "\n\t*\t".join(validate_msgs)
                raise ValidationError(msg)


        res = super().button_confirm()

        for po in self:
            for line in po.order_line:
                product = line.product_id
                vendor = po.partner_id

                # Search existing supplierinfo
                supplierinfo = self.env['product.supplierinfo'].search([
                    ('partner_id', '=', vendor.id),
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ], limit=1)

                vals = {
                    'price': line.price_unit,
                    'last_purchase_date': fields.Date.today(),
                    'unit_rate': line.unit_rate,
                    'currency_id': po.currency_id.id,
                    'discount': line.discount
                }

                product.product_tmpl_id.standard_price = line.unit_rate

                if supplierinfo:
                    # ✅ Update existing record
                    supplierinfo.write(vals)
        return res


class PurchaseOrderLine(models.Model):
    _inherit  = 'purchase.order.line'

    unit_rate = fields.Float(
        string="Unit Rate",
        compute="_compute_unit_rate",
        store=True
    )
    price_unit = fields.Float(string="LP")
    purchase_for_id = fields.Many2one('purchase.for', string="Pur. For")

    @api.depends('price_unit', 'product_qty', 'discount')
    def _compute_unit_rate(self):
        for line in self:
            if line.product_qty:
                total_after_discount = line.price_unit * line.product_qty * (1 - (line.discount or 0) / 100)
                line.unit_rate = total_after_discount / line.product_qty
            else:
                line.unit_rate = line.price_unit