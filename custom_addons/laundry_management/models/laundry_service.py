from odoo import models,fields,api

class LaundryService(models.Model):
    _name = 'laundry.service'
    _description = 'Laundry Service'

    name = fields.Char(required=True)
    price = fields.Float(required=True)
    unit = fields.Selection(
        selection=[
            ('kg', 'Kg'),
            ('item', 'Item')
        ],required=True
    )
    active = fields.Boolean(default=True)
    description = fields.Text()
