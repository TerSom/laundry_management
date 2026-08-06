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
    consumable_product_ids = fields.Many2many('product.product',string='Consumables')
    need_wash = fields.Boolean(default=False)
    need_dry = fields.Boolean(default=False)
    need_iron = fields.Boolean(default=False)
    wash_duration = fields.Float(default=0.0 ,string='Wash Duration (Hours)')
    dry_duration = fields.Float(default=0.0, string='Dry Duration (Hours)')
    iron_duration = fields.Float(default=0.0, string='Iron Duration (Hours)')

    @api.onchange('need_wash','need_dry','need_iron')
    def _onchange_need_wash(self):
        if self.need_wash:
            self.wash_duration = 0.45
        elif self.need_dry:
            self.dry_duration = 0.45
        elif self.need_iron:
            self.iron_duration = 0.15

