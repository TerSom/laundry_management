from odoo import models,fields

class GoldPrice(models.Model):
    _name = "gold.price"
    _description = "Gold Price"
    _order = 'fetch_date desc'

    name = fields.Char(string="Name", required=True)
    price = fields.Float(string="Price", required=True)
    currency = fields.Char(string="Currency", required=True)
    fetch_date = fields.Datetime(string="Fetch Date", default=fields.Datetime.now())
