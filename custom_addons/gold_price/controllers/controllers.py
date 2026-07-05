import requests
import json
from odoo import http
from odoo.http import request


class EstateGoldPriceController(http.Controller):

    @http.route('/estate/gold_price', type='http', auth='public', methods=['GET'], csrf=False)
    def get_gold_price(self, **kwargs):
        try:
            response = requests.get('https://api.gold-api.com/price/XAU', timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            data = {'error': str(e)}

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )