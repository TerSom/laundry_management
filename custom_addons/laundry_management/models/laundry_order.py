from odoo import models,fields,api,Command
from odoo.exceptions import ValidationError
from datetime import timedelta

class LaundryOrder(models.Model):
    _name = 'laundry.order'
    _description = 'Laundry Order'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string="Order Number", required=True, copy=False, readonly=True, default="New")
    partner_id = fields.Many2one('res.partner', string="Customer",required=True)
    date_received = fields.Date(string='Start Date',default=fields.Date.today)
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('received','Received'),
            ('washing','Washing'),
            ('drying','Drying'),
            ('ironing','Ironing'),
            ('ready','Ready'),
            ('delivered','Delivered')
        ],
        default='draft',
        string='Status'
    )
    line_ids = fields.One2many('laundry.order.line', 'order_id', string="Order Lines")
    total_price = fields.Float(
        compute="_compute_total"
    )
    order_count = fields.Integer(
        compute="_compute_order_count"
    )
    invoice_id = fields.Many2one('account.move', string="invoice", readonly=True, copy=False)
    delivered_date = fields.Datetime(readonly=False,string="Delivered Date")

    @api.depends('partner_id')
    def _compute_order_count(self):
        for record in self:
            record.order_count = self.env['laundry.order'].search_count([
                ("partner_id", "=", record.partner_id.id)
            ])

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for record in self:
            record.total_price = sum(record.line_ids.mapped('subtotal'))

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env['ir.sequence'].next_by_code("laundry.order") or "New"

        return super().create(vals_list)

    def action_received(self):
        for record in self:
            record.state = "received"

    def action_washing(self):
        for record in self:
            record.state = 'washing'

    def action_drying(self):
        for record in self:
            record.state = 'drying'

    def action_ironing(self):
        for record in self:
            record.state = 'ironing'

    def action_ready(self):
        for record in self:
            record.state = 'ready'

    def action_delivered(self):
        for record in self:
            if not record.partner_id:
                raise ValidationError("Please select a customer first.")

            if not record.line_ids:
                raise ValidationError("Please add at least one service.")

            invoice_lines = []
            for line in record.line_ids:
                invoice_lines.append(
                    Command.create({
                        'name': line.service_id.name,
                        'quantity': line.quantity,
                        'price_unit': line.price_unit,
                    })
                )

            invoice = self.env['account.move'].create({
                'partner_id': record.partner_id.id,
                'invoice_date': fields.Date.today(),
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
            })

            record.invoice_id = invoice
            record.state = 'delivered'
            record.delivered_date = fields.Datetime.now()

        return {
            "type": "ir.actions.act_window",
            "name": "Customer Invoice",
            "res_model": "account.move",
            "res_id": invoice.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_customer_order(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Customer Orders",
            "res_model": "laundry.order",
            "view_mode": "list,form",
            "domain": [
            ("partner_id", "=", self.partner_id.id)
            ],
        }

    def action_send_email(self):
        self.ensure_one()

        template = self.env.ref(
            "laundry_management.email_template_laundry_ready"
        )

        template.send_mail(self.id, force_send=True)

    def cron_send_reminder(self):
        limit_date = fields.Datetime.now() - timedelta(days=3)

        orders = self.search([
            ("state", "=", "delivered"),
            ("delivered_date", "<=", limit_date),
        ])

        template = self.env.ref(
            "laundry_management.email_template_reminder"
        )

        for order in orders:
            template.send_mail(order.id, force_send=True)