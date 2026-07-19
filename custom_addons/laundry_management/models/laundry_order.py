from odoo import models,fields,api

class LaundryOrder(models.Model):
    _name = 'laundry.order'
    _description = 'Laundry Order'

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
            record.state = 'delivered'

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

