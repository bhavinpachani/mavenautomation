from odoo import models, fields, _
import base64
import io
import re
from openpyxl import load_workbook
from openpyxl.styles import Font


class VerifyBOMWizard(models.TransientModel):
    _name = 'verify.bom.wizard'
    _description = 'Verify BOM Wizard'

    file = fields.Binary(string="Upload BOM File", required=True)
    file_name = fields.Char()

    result_message = fields.Text()
    updated_file = fields.Binary()
    updated_file_name = fields.Char()

    def action_verify(self):
        self.ensure_one()

        if not self.file:
            return

        file_data = base64.b64decode(self.file)
        input_stream = io.BytesIO(file_data)

        wb = load_workbook(input_stream)
        sheet = wb.active

        product_model = self.env['product.template']

        red_font = Font(color="FFFF0000")
        green_font = Font(color="FF00B050")
        default_font = Font(color="000000")

        def clean(val):
            if not val:
                return None
            val = str(val)

            match = re.search(r"\]\s*(.+)", val)
            if match:
                val = match.group(1)

            return val.strip()

        all_valid = True

        for row in sheet.iter_rows(min_row=2):

            if not row or len(row) < 3:
                continue

            col0 = row[0]
            col1 = row[1]
            qty = row[2]

            val0 = clean(col0.value)
            val1 = clean(col1.value)

            # -----------------------------
            # ROW[0] CHECK
            # -----------------------------
            found0 = True  # default TRUE if empty (prevents false failure)

            if val0:
                found0 = bool(product_model.search([
                    ('name', 'ilike', val0)
                ], limit=1))

            if found0:
                col0.font = green_font
            else:
                col0.font = red_font
                all_valid = False

            # Convert to uppercase for import compatibility
            if val0:
                col0.value = val0.upper()

            # -----------------------------
            # ROW[1] CHECK
            # -----------------------------
            found1 = True  # default TRUE if empty

            if val1:
                found1 = bool(product_model.search([
                    ('name', 'ilike', val1)
                ], limit=1))

            if found1:
                col1.font = green_font
            else:
                col1.font = red_font
                all_valid = False

            # Convert to uppercase for import compatibility
            if val1:
                col1.value = val1.upper()

            # -----------------------------
            # NEVER TOUCH QTY
            # -----------------------------
            qty.font = default_font

        # -----------------------------
        # SAVE FILE
        # -----------------------------
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        self.updated_file = base64.b64encode(output.read())
        self.updated_file_name = "bom_verified.xlsx"

        # -----------------------------
        # FINAL MESSAGE (FIXED)
        # -----------------------------
        self.result_message = (
            "File verified successfully."
            if all_valid
            else "Some products are missing. Please check file."
        )

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'verify.bom.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_download(self):
        self.ensure_one()

        if not self.updated_file:
            return

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=verify.bom.wizard&id={self.id}&field=updated_file&filename_field=updated_file_name&download=true',
            'target': 'self',
        }