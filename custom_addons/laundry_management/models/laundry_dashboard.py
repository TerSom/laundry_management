from odoo import api, fields, models


class LaundryDashboard(models.TransientModel):
    _name = "laundry.dashboard"
    _description = "Laundry Dashboard"

    total_orders = fields.Integer(string="Total Pesanan", readonly=True)
    total_customers = fields.Integer(string="Total Pelanggan", readonly=True)
    total_revenue = fields.Float(string="Total Pendapatan", readonly=True)

    pending_orders = fields.Integer(string="Pesanan Pending", readonly=True)
    processing_orders = fields.Integer(string="Pesanan Processing", readonly=True)
    delivered_orders = fields.Integer(string="Pesanan Delivered", readonly=True)

    @api.model
    def get_dashboard(self):
        order_model = self.env["laundry.order"]
        
        all_orders = order_model.search([])
        pending = order_model.search_count([("state", "in", ["ready",'draft'])])
        processing = order_model.search_count([("state", "in", ["received","washing",'drying','ironing'])])
        delivered = order_model.search_count([("state", "=", "delivered")])
        
        total_revenue = sum(all_orders.mapped("total_price")) if all_orders else 0.0
        unique_customers = len(set(all_orders.mapped("partner_id").ids)) if all_orders else 0

        return self.create({
            "total_orders": len(all_orders),
            "total_customers": unique_customers,
            "total_revenue": total_revenue,
            "pending_orders": pending,
            "processing_orders": processing,
            "delivered_orders": delivered,
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