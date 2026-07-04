import io
import base64
import xlsxwriter

from odoo import models


class EstateProperty(models.Model):
    _inherit = "estate.property"

    def action_export_excel(self):
        self.ensure_one()

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Property")

        header = workbook.add_format({
            "bold": True,
            "bg_color": "#D9EAD3",
            "border": 1,
        })

        cell = workbook.add_format({
            "border": 1,
        })

        date_format = workbook.add_format({
            "border": 1,
            "num_format": "dd/mm/yyyy",
        })

        money_format = workbook.add_format({
            "border": 1,
            "num_format": "#,##0.00",
        })

        # Header
        sheet.write(0, 0, "Name", header)
        sheet.write(0, 1, "PostCode", header)
        sheet.write(0, 2, "Date Availability", header)
        sheet.write(0, 3, "Expected Price", header)
        sheet.write(0, 4, "Selling Price", header)
        sheet.write(0, 5, "State", header)

        # Data
        sheet.write(1, 0, self.name, cell)
        sheet.write(1, 1, self.postcode, cell)
        sheet.write(1, 2, self.date_availability, date_format)
        sheet.write(1, 3, self.expected_price, money_format)
        sheet.write(1, 4, self.selling_price, money_format)
        sheet.write(1, 5, dict(self._fields['state'].selection).get(self.state, self.state), cell)

        sheet.set_column("A:A", 20)
        sheet.set_column("B:C", 18)
        sheet.set_column("D:E", 15)
        sheet.set_column("F:F", 15)

        workbook.close()

        output.seek(0)

        attachment = self.env["ir.attachment"].create({
            "name": f"{self.name} Report Excel .xlsx",
            "type": "binary",
            "datas": base64.b64encode(output.read()),
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }