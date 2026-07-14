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

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for record in self:
            record.total_price = sum(record.line_ids.mapped('subtotal'))

