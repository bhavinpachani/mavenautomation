# -*- coding: utf-8 -*-

import base64
import csv
import io
import re
from datetime import datetime

import xlrd
import xlwt

from odoo import _, fields, models
from odoo.exceptions import UserError


IMPORT_HEADERS = [
    'Product',
    'Quantity',
    'Unit',
    'Del. Time',
    'LP',
    'Disc.%',
    'Unit Rate',
    'Amount',
    'Taxes',
]

HEADER_ALIASES = {
    'PRODUCT': 'PRODUCT',
    'QUANTITY': 'QUANTITY',
    'QTY': 'QUANTITY',
    'UNIT': 'UNIT',
    'UOM': 'UNIT',
    'DEL. TIME': 'DEL. TIME',
    'DEL TIME': 'DEL. TIME',
    'DELIVERY TIME': 'DEL. TIME',
    'CUSTOMER LEAD': 'DEL. TIME',
    'LP': 'LP',
    'LIST PRICE': 'LP',
    'DISC.%': 'DISC.%',
    'DISC%': 'DISC.%',
    'DISCOUNT': 'DISC.%',
    'DISC': 'DISC.%',
    'UNIT RATE': 'UNIT RATE',
    'PRICE': 'UNIT RATE',
    'PRICE UNIT': 'UNIT RATE',
    'AMOUNT': 'AMOUNT',
    'TAXES': 'TAXES',
    'TAX': 'TAXES',
}


class ImportSaleOrderLineWizard(models.TransientModel):
    _name = 'import.sale.order.line.wizard'
    _description = 'Import Sale Order Line Wizard'

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
        required=True,
        readonly=True,
    )
    file = fields.Binary(string='Upload File')
    file_name = fields.Char(string='File Name')
    not_imported_file = fields.Binary(string='Not Imported File', readonly=True)
    not_imported_filename = fields.Char(string='Not Imported Filename', readonly=True)
    import_message = fields.Text(string='Result', readonly=True)

    def action_import(self):
        self.ensure_one()
        order = self.sale_order_id
        if not order:
            raise UserError(_('Sale Order is required.'))
        if order.state != 'draft':
            raise UserError(_('Sale order lines can only be imported on draft quotations.'))
        if not self.file:
            raise UserError(_('Please upload a .xls, .xlsx, or .csv file.'))

        rows = self._parse_file_rows()
        if not rows:
            raise UserError(_('No data found in the uploaded file.'))

        imported_count = 0
        not_imported = []
        existing_line_keys = {
            self._line_key(line.product_id.id, line.product_uom_qty, line.price_unit, line.discount)
            for line in order.order_line
            if line.product_id
        }

        for row in rows:
            result = self._process_row(order, row, existing_line_keys)
            if result['imported']:
                imported_count += 1
                if result.get('line_key'):
                    existing_line_keys.add(result['line_key'])
            else:
                not_imported.append(result)

        vals = {
            'import_message': False,
            'not_imported_file': False,
            'not_imported_filename': False,
            'file': False,
            'file_name': False,
        }

        if not_imported:
            vals.update(self._prepare_not_imported_file(not_imported))
            if imported_count:
                vals['import_message'] = _(
                    '%(imported)s line(s) imported successfully. '
                    '%(failed)s line(s) could not be imported. '
                    'Please download not_imported.xls.',
                    imported=imported_count,
                    failed=len(not_imported),
                )
            else:
                vals['import_message'] = _(
                    'No lines were imported. Please download not_imported.xls '
                    'and fix the highlighted values.'
                )
            self.write(vals)
            return {
                'type': 'ir.actions.act_window',
                'name': _('Import Sale Order Lines'),
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
            }

        self.write(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('File imported successfully.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _normalize_header(self, header):
        value = str(header or '').strip().upper()
        value = re.sub(r'\s+', ' ', value)
        return HEADER_ALIASES.get(value, value)

    def _cell_value(self, value):
        if value is None:
            return ''
        if isinstance(value, float) and value == int(value):
            return str(int(value))
        return str(value).strip()

    def _normalize_name(self, value):
        """Collapse repeated spaces for reliable matching (e.g. CGST  9% -> CGST 9%)."""
        return re.sub(r'\s+', ' ', self._cell_value(value)).strip()

    def _parse_float(self, value, default=0.0):
        if value in (None, False, ''):
            return default
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip()
        text = text.replace(',', '')
        text = re.sub(r'[^\d.\-]', '', text)
        if not text or text in ('-', '.', '-.'):
            return default
        try:
            return float(text)
        except ValueError:
            return default

    def _parse_file_rows(self):
        file_data = base64.b64decode(self.file)
        filename = (self.file_name or '').lower()

        if filename.endswith('.csv'):
            return self._parse_csv(file_data)
        if filename.endswith('.xlsx'):
            return self._parse_xlsx(file_data)
        if filename.endswith('.xls'):
            return self._parse_xls(file_data)
        raise UserError(_('Unsupported file format. Please upload a .csv, .xls, or .xlsx file.'))

    def _rows_from_matrix(self, headers, matrix_rows):
        data_rows = []
        for row in matrix_rows:
            row_dict = {}
            has_value = False
            for idx, header in enumerate(headers):
                if not header:
                    continue
                value = row[idx] if idx < len(row) else ''
                row_dict[header] = value
                if self._cell_value(value):
                    has_value = True
            if has_value:
                data_rows.append(row_dict)
        return data_rows

    def _parse_csv(self, file_data):
        try:
            text = file_data.decode('utf-8-sig')
        except UnicodeDecodeError:
            text = file_data.decode('latin-1')
        reader = csv.reader(io.StringIO(text))
        rows = list(reader)
        if not rows:
            raise UserError(_('The uploaded file is empty.'))
        headers = [self._normalize_header(h) for h in rows[0]]
        if 'PRODUCT' not in headers:
            raise UserError(_('The file must contain a Product column.'))
        return self._rows_from_matrix(headers, rows[1:])

    def _parse_xls(self, file_data):
        try:
            workbook = xlrd.open_workbook(file_contents=file_data)
        except Exception as exc:
            raise UserError(_('Unable to read Excel file: %s', exc)) from exc

        sheet = workbook.sheet_by_index(0)
        if sheet.nrows < 2:
            raise UserError(_('The uploaded file has no data rows.'))

        headers = [self._normalize_header(sheet.cell_value(0, col)) for col in range(sheet.ncols)]
        if 'PRODUCT' not in headers:
            raise UserError(_('The file must contain a Product column.'))

        matrix_rows = []
        for row_idx in range(1, sheet.nrows):
            row_values = []
            for col_idx in range(sheet.ncols):
                cell = sheet.cell(row_idx, col_idx)
                if cell.ctype == xlrd.XL_CELL_DATE:
                    value = datetime(*xlrd.xldate_as_tuple(cell.value, workbook.datemode))
                    row_values.append(value.strftime('%Y-%m-%d'))
                else:
                    row_values.append(cell.value)
            matrix_rows.append(row_values)
        return self._rows_from_matrix(headers, matrix_rows)

    def _parse_xlsx(self, file_data):
        try:
            from openpyxl import load_workbook
        except ImportError as exc:
            raise UserError(_('openpyxl is required to import .xlsx files.')) from exc

        workbook = load_workbook(io.BytesIO(file_data), read_only=True, data_only=True)
        sheet = workbook.active
        rows = list(sheet.iter_rows(values_only=True))
        if not rows:
            raise UserError(_('The uploaded file is empty.'))

        headers = [self._normalize_header(cell) for cell in rows[0]]
        if 'PRODUCT' not in headers:
            raise UserError(_('The file must contain a Product column.'))

        matrix_rows = []
        for row in rows[1:]:
            values = []
            for value in row:
                if isinstance(value, datetime):
                    values.append(value.strftime('%Y-%m-%d'))
                else:
                    values.append(value)
            matrix_rows.append(values)
        return self._rows_from_matrix(headers, matrix_rows)

    def _line_key(self, product_id, quantity, price_unit, discount):
        return (
            product_id,
            round(float(quantity or 0.0), 6),
            round(float(price_unit or 0.0), 6),
            round(float(discount or 0.0), 6),
        )

    def _split_product_value(self, value):
        text = self._cell_value(value)
        if not text:
            return '', ''
        if ' / ' in text:
            code, name = text.split(' / ', 1)
            return code.strip(), name.strip()
        return text, text

    def _find_product(self, product_value):
        Product = self.env['product.product']
        raw = self._cell_value(product_value)
        if not raw:
            return Product.browse()

        code, name = self._split_product_value(raw)
        domain_company = ['|', ('company_id', '=', False), ('company_id', '=', self.sale_order_id.company_id.id)]

        product = Product.search([('default_code', '=', code)] + domain_company, limit=1)
        if not product and code != name:
            product = Product.search([('default_code', '=', name)] + domain_company, limit=1)
        if not product:
            product = Product.search([('name', '=ilike', name)] + domain_company, limit=1)
        if not product:
            product = Product.search([('name', '=ilike', raw)] + domain_company, limit=1)
        if not product:
            product = Product.search([('default_code', '=ilike', raw)] + domain_company, limit=1)
        return product

    def _find_uom(self, uom_name, product):
        if not uom_name:
            return product.uom_id
        uom = self.env['uom.uom'].search([('name', '=ilike', self._cell_value(uom_name))], limit=1)
        return uom

    def _parse_tax_names(self, tax_value):
        """Split multi-tax cells like 'SGST 9%,CGST  9%' or 'SGST 9%; CGST 9%'."""
        text = self._cell_value(tax_value)
        if not text:
            return []
        # Prefer comma / semicolon / pipe separators for multiple taxes.
        parts = re.split(r'[,;|]+', text)
        names = []
        for part in parts:
            name = self._normalize_name(part)
            if name:
                names.append(name)
        return names

    def _find_tax_by_name(self, tax_name, company):
        """Find a sale tax by name; avoid ILIKE wildcard issues with '%' in tax names."""
        Tax = self.env['account.tax']
        target = self._normalize_name(tax_name).lower()
        if not target:
            return Tax.browse()

        candidates = Tax.search([
            ('company_id', '=', company.id),
            ('type_tax_use', '=', 'sale'),
        ])
        tax = candidates.filtered(lambda t: self._normalize_name(t.name).lower() == target)[:1]
        if tax:
            return tax

        # Fallback: company taxes without sale type restriction.
        candidates = Tax.search([('company_id', '=', company.id)])
        tax = candidates.filtered(lambda t: self._normalize_name(t.name).lower() == target)[:1]
        return tax

    def _resolve_taxes(self, tax_value):
        """Return (tax_records, tax_status_list) for comma/semicolon separated taxes."""
        company = self.sale_order_id.company_id
        status_list = []
        found_taxes = self.env['account.tax']

        for tax_name in self._parse_tax_names(tax_value):
            tax = self._find_tax_by_name(tax_name, company)
            status_list.append({
                'name': tax_name,
                'found': bool(tax),
                'tax': tax,
            })
            if tax:
                found_taxes |= tax
        return found_taxes, status_list

    def _process_row(self, order, row, existing_line_keys):
        product_value = row.get('PRODUCT', '')
        product = self._find_product(product_value)
        taxes, tax_status = self._resolve_taxes(row.get('TAXES', ''))
        quantity = self._parse_float(row.get('QUANTITY', 0), 0.0)
        unit_rate = self._parse_float(row.get('UNIT RATE', ''), None)
        if unit_rate is None:
            unit_rate = self._parse_float(row.get('LP', 0), 0.0)
        discount = self._parse_float(row.get('DISC.%', 0), 0.0)
        customer_lead = str(row.get('DEL. TIME', ''))
        amount = self._cell_value(row.get('AMOUNT', ''))
        unit_name = self._cell_value(row.get('UNIT', ''))
        lp_value = self._cell_value(row.get('LP', ''))
        price_unit = unit_rate or 0.0

        failure_reasons = []
        product_found = bool(product)
        taxes_ok = all(item['found'] for item in tax_status) if tax_status else True
        line_key = False

        if not self._cell_value(product_value):
            failure_reasons.append('missing_product')
        elif not product_found:
            failure_reasons.append('product_not_found')
        else:
            line_key = self._line_key(product.id, quantity, price_unit, discount)
            if line_key in existing_line_keys:
                failure_reasons.append('already_imported')

        if quantity <= 0:
            failure_reasons.append('invalid_quantity')

        uom = False
        if product_found:
            uom = self._find_uom(unit_name, product)
            if unit_name and not uom:
                failure_reasons.append('uom_not_found')
            elif not uom:
                uom = product.uom_id

        if tax_status and not taxes_ok:
            failure_reasons.append('tax_not_found')

        export_row = {
            'Product': self._cell_value(product_value),
            'Quantity': quantity,
            'Unit': unit_name,
            'Del. Time': customer_lead,
            'LP': lp_value,
            'Disc.%': discount,
            'Unit Rate': unit_rate if unit_rate is not None else '',
            'Amount': amount,
            'Taxes': self._cell_value(row.get('TAXES', '')),
            'product_found': product_found,
            'tax_status': tax_status,
            'reason': ', '.join(failure_reasons),
        }

        if failure_reasons:
            return {
                'imported': False,
                'product_id': product.id if product else False,
                'line_key': line_key,
                'export_row': export_row,
            }

        line_vals = {
            'order_id': order.id,
            'product_id': product.id,
            'product_uom_qty': quantity,
            'product_uom_id': uom.id,
            'price_unit': price_unit,
            'discount': discount,
            'lead_time': customer_lead,
        }
        if taxes:
            line_vals['tax_ids'] = [(6, 0, taxes.ids)]

        self.env['sale.order.line'].create(line_vals)
        return {
            'imported': True,
            'product_id': product.id,
            'line_key': line_key,
            'export_row': export_row,
        }

    def _font_style(self, colour_index=None, bold=False):
        style = xlwt.XFStyle()
        font = xlwt.Font()
        if colour_index is not None:
            font.colour_index = colour_index
        font.bold = bold
        style.font = font
        return style

    def _prepare_not_imported_file(self, not_imported):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Not Imported')

        header_style = self._font_style(bold=True)
        red_style = self._font_style(colour_index=xlwt.Style.colour_map['red'])
        green_style = self._font_style(colour_index=xlwt.Style.colour_map['green'])
        default_style = self._font_style()

        for col, header in enumerate(IMPORT_HEADERS):
            sheet.write(0, col, header, header_style)
            sheet.col(col).width = 4000

        for row_idx, item in enumerate(not_imported, start=1):
            export_row = item['export_row']
            product_style = green_style if export_row.get('product_found') else red_style

            sheet.write(row_idx, 0, export_row.get('Product', ''), product_style)
            sheet.write(row_idx, 1, export_row.get('Quantity', ''), default_style)
            sheet.write(row_idx, 2, export_row.get('Unit', ''), default_style)
            sheet.write(row_idx, 3, export_row.get('Del. Time', ''), default_style)
            sheet.write(row_idx, 4, export_row.get('LP', ''), default_style)
            sheet.write(row_idx, 5, export_row.get('Disc.%', ''), default_style)
            sheet.write(row_idx, 6, export_row.get('Unit Rate', ''), default_style)
            sheet.write(row_idx, 7, export_row.get('Amount', ''), default_style)

            tax_status = export_row.get('tax_status') or []
            if not tax_status:
                sheet.write(row_idx, 8, export_row.get('Taxes', ''), default_style)
            else:
                # Write each tax name with its own color using rich text is limited in xlwt;
                # if all found -> green, if none found -> red, mixed -> write semicolon list
                # with overall red when any missing, else green. Also append missing markers.
                tax_names = []
                all_found = True
                any_found = False
                for status in tax_status:
                    tax_names.append(status['name'])
                    if status['found']:
                        any_found = True
                    else:
                        all_found = False
                tax_text = ', '.join(tax_names)
                if all_found and any_found:
                    sheet.write(row_idx, 8, tax_text, green_style)
                elif not any_found:
                    sheet.write(row_idx, 8, tax_text, red_style)
                else:
                    # Mixed: mark missing taxes with [MISSING]
                    mixed_parts = []
                    for status in tax_status:
                        if status['found']:
                            mixed_parts.append(status['name'])
                        else:
                            mixed_parts.append('%s [MISSING]' % status['name'])
                    sheet.write(row_idx, 8, ', '.join(mixed_parts), red_style)

        buffer = io.BytesIO()
        workbook.save(buffer)
        return {
            'not_imported_file': base64.b64encode(buffer.getvalue()),
            'not_imported_filename': 'not_imported.xls',
        }
