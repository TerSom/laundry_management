from odoo import models,fields,api

class LaundryOrderLine(models.Model):
    _name = 'laundry.order.line'
    _description = 'Laundry Order Line'

    order_id = fields.Many2one('laundry.order', string='Order', required=True, ondelete="cascade")
    service_id = fields.Many2one('laundry.service', string='service', required=True)
    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price")
    subtotal = fields.Float(
        compute = "_compute_subtotal",
        store=True
    )

    @api.depends('price_unit','quantity')
    def _compute_subtotal(self):
        for record in self:
            record.subtotal = record.quantity * record.price_unit

    @api.onchange('service_id')
    def _onchange_service(self):
        for record in self:
            record.price_unit = record.service_id.price