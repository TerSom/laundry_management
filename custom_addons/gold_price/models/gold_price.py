from odoo import fields, models
import requests
from dotenv import load_dotenv
import os

class GoldPrice(models.Model):
    _name = "gold.price"
    _description = "Gold Price"

    symbol = fields.Char()
    name = fields.Char()
    price = fields.Float()
    currency = fields.Char()
    updated_at = fields.Char()


    def cron_sync_gold_price(self):

        url = os.getenv("URL")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        self.create({
            "symbol": data.get("symbol"),
            "name": data.get("name"),
            "price": data.get("price"),
            "currency": data.get("currency"),
            "updated_at": data.get("updatedAt"),
        })