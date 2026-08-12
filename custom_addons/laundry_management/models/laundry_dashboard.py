from odoo import api, fields, models
from datetime import datetime, time


class LaundryDashboard(models.TransientModel):
    _name = "laundry.dashboard"
    _description = "Laundry Dashboard"

    # Global KPI
    total_orders = fields.Integer(string="Total Pesanan", readonly=True)
    total_customers = fields.Integer(string="Total Pelanggan", readonly=True)
    total_revenue = fields.Float(string="Total Pendapatan", readonly=True)

    # Today KPI
    daily_orders = fields.Integer(string="Pesanan Hari Ini", readonly=True)
    daily_revenue = fields.Float(string="Pendapatan Hari Ini", readonly=True)
    avg_completion_time = fields.Float(string="Rata-rata Waktu Selesai (Jam)", readonly=True)

    # Status KPI
    pending_orders = fields.Integer(string="Pesanan Pending", readonly=True)
    processing_orders = fields.Integer(string="Pesanan Processing", readonly=True)
    delivered_orders = fields.Integer(string="Pesanan Delivered", readonly=True)

    # Summary
    top_services = fields.Char(string="Layanan Terpopuler", readonly=True)
    
    # Dynamic Field untuk menggantikan t-esc di XML Odoo 18
    last_updated = fields.Char(string="Terakhir Diperbarui", readonly=True)

    @api.model
    def get_dashboard(self):
        order_model = self.env["laundry.order"]
        order_line_model = self.env["laundry.order.line"]

        # Time range for today
        today_start = datetime.combine(fields.Date.today(), time.min)
        today_end = datetime.combine(fields.Date.today(), time.max)

        # Basic statistics
        all_orders = order_model.search([])
        daily_order_recs = order_model.search([
            ("date_received", ">=", today_start),
            ("date_received", "<=", today_end)
        ])

        # Status counts
        pending = order_model.search_count([("state", "in", ["draft", "ready"])])
        processing = order_model.search_count([("state", "in", ["received", "washing", "drying", "ironing"])])
        delivered = order_model.search_count([("state", "=", "delivered")])

        # Revenue and Customers
        total_revenue = sum(all_orders.mapped("total_price")) if all_orders else 0.0
        daily_revenue = sum(daily_order_recs.mapped("total_price")) if daily_order_recs else 0.0
        unique_customers = len(set(all_orders.mapped("partner_id").ids)) if all_orders else 0

        # Efficiency: Average completion time in hours
        delivered_recs = order_model.search([
            ("state", "=", "delivered"),
            ("delivered_date", "!=", False),
            ("date_received", "!=", False)
        ])

        avg_time = 0.0
        if delivered_recs:
            durations = [
                (rec.delivered_date - rec.date_received).total_seconds() / 3600.0
                for rec in delivered_recs
            ]
            avg_time = sum(durations) / len(durations)

        # Top Services aggregation
        top_lines = order_line_model.read_group(
            domain=[],
            fields=["service_id", "quantity:sum"],
            groupby=["service_id"],
            orderby="quantity desc",
            limit=3
        )

        top_services_list = []
        for line in top_lines:
            if line.get('service_id'):
                service_name = self.env['laundry.service'].browse(line['service_id'][0]).name
                top_services_list.append(f"{service_name} ({int(line['quantity'])})")

        top_services_str = ", ".join(top_services_list) if top_services_list else "-"

        # Waktu lokal ter-format
        now_str = fields.Datetime.context_timestamp(self, datetime.now()).strftime('%Y-%m-%d %H:%M:%S')

        return self.create({
            "total_orders": len(all_orders),
            "total_customers": unique_customers,
            "total_revenue": total_revenue,
            "daily_orders": len(daily_order_recs),
            "daily_revenue": daily_revenue,
            "avg_completion_time": round(avg_time, 2),
            "pending_orders": pending,
            "processing_orders": processing,
            "delivered_orders": delivered,
            "top_services": top_services_str,
            "last_updated": now_str,
        })

    @api.model
    def open_dashboard(self):
        dashboard = self.get_dashboard()

        return {
            "type": "ir.actions.act_window",
            "name": "Laundry Dashboard",
            "res_model": "laundry.dashboard",
            "view_mode": "form",
            "res_id": dashboard.id,
            "target": "current",
        }