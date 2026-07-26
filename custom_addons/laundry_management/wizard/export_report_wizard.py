import io
import base64
import xlsxwriter

from odoo import fields, models


class ExportReportWizard(models.TransientModel):
    _name = "export.report.wizard"
    _description = "Export Laundry Report"

    date_from = fields.Date(
        string="From Date",
        required=True,
    )

    date_to = fields.Date(
        string="To Date",
        required=True,
    )

    state = fields.Selection([
        ("received", "Received"),
        ("washing", "Washing"),
        ("drying", "Drying"),
        ("ironing", "Ironing"),
        ("ready", "Ready"),
        ("delivered", "Delivered"),
    ], string="Status")

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
    )

    def action_export_excel(self):
        self.ensure_one()

        domain = [
            ("date_received", ">=", self.date_from),
            ("date_received", "<=", self.date_to),
        ]

        if self.state:
            domain.append(("state", "=", self.state))

        if self.partner_id:
            domain.append(("partner_id", "=", self.partner_id.id))

        orders = self.env["laundry.order"].search(domain)

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        sheet = workbook.add_worksheet("Laundry Report")

        header = workbook.add_format({
            "bold": True,
            "bg_color": "#1F497D",
            "font_color" : "#ffff",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        })
        cell = workbook.add_format({
            "border": 1,
        })
        date_format = workbook.add_format({
            "num_format": "YYYY-MM-DD",
            "align": "left",
        })

        date_format_cell = workbook.add_format({
            "border" : 1,
            "num_format": "YYYY-MM-DD",
            "align": "left",
        })
        money_format = workbook.add_format({
            "border": 1,
            "num_format": '"Rp" #,##0.00',
        })

        # Header
        sheet.merge_range("A1:E1", "Laundry Order Report", header)
        sheet.write(2 , 0, "Date From:", )
        sheet.write(3 , 0, "Status:", )
        sheet.write(2 , 3, "Date to:", )
        sheet.write(3 , 3, "Customer:", )

        sheet.write_datetime(2, 1 , self.date_from, date_format)
        sheet.write_datetime(2, 4, self.date_to, date_format)
        sheet.write(3, 1 , self.state)
        sheet.write(3, 4, self.partner_id.name)

        # Header Table
        sheet.write(5, 0, "Order", header)
        sheet.write(5, 1, "Customer", header)
        sheet.write(5, 2, "Date", header)
        sheet.write(5, 3, "Status", header)
        sheet.write(5, 4, "Total", header)

        # Data
        state_labels = dict(self._fields["state"].selection)
        row = 6
        for order in orders:
            sheet.write(row, 0, order.name, cell)
            sheet.write(row, 1, order.partner_id.name or "", cell)
            if order.date_received:
                sheet.write_datetime(row, 2, order.date_received, date_format_cell )
            else:
                sheet.write(row, 2, "", cell)
            sheet.write(
                row, 3,
                state_labels.get(order.state, order.state),
                cell,
            )
            sheet.write(row, 4, order.total_price, money_format)
            row += 1

        sheet.set_column("A:A", 15)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:C", 15)
        sheet.set_column("D:D", 15)
        sheet.set_column("E:E", 15)

        workbook.close()
        output.seek(0)

        attachment = self.env["ir.attachment"].create({
            "name": "Laundry_Report.xlsx",
            "type": "binary",
            "datas": base64.b64encode(output.read()),
            "mimetype": (
                "application/vnd.openxmlformats-officedocument"
                ".spreadsheetml.sheet"
            ),
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }