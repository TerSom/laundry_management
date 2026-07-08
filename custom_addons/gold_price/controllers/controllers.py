import json
import requests

from odoo import http
from odoo.http import request


class GoldPriceController(http.Controller):

# get api
    @http.route(
        ['/api/gold_price_get/'],
        type='http',
        auth='public',
        methods=['GET'],
        csrf=False
    )
    def gold_price_get(self, **params):
        url = "https://api.gold-api.com/price/XAU"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            return http.Response(
                json.dumps({
                    "status": 200,
                    "message": "Success",
                    "data": data
                }, indent=4, default=str),
                content_type="application/json",
                status=200
            )

        except requests.exceptions.RequestException as e:
            return http.Response(
                json.dumps({
                    "status": 500,
                    "message": str(e)
                }),
                content_type="application/json",
                status=500
            )

# post api
    @http.route(
        ['/api/local_gold_price/'],
        type='http',
        auth='public',
        methods=['POST'],
        csrf=False
    )
    def local_gold_price(self, **params):
        url = "http://localhost:8018/api/gold_price_get/"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            result = response.json()
            data = result.get("data", {})

            request.env["gold.price"].sudo().create({
                "symbol": data.get("symbol"),
                "name": data.get("name"),
                "price": data.get("price"),
                "currency": data.get("currency"),
                "updated_at": data.get("updatedAt"),
            })

            return http.Response(
                json.dumps({
                    "status": 200,
                    "message": "Data berhasil disimpan ke Odoo",
                    "data": data
                }, default=str),
                content_type="application/json",
                status=200
            )

        except requests.exceptions.RequestException as e:
            return http.Response(
                json.dumps({
                    "status": 500,
                    "message": str(e)
                }),
                content_type="application/json",
                status=500
            )

# put api 
    @http.route(
    ['/api/gold_price_put/'],
    type='http',
    auth='public',
    methods=['PUT'],
    csrf=False
    )
    def gold_price_put(self, **params):
        data = json.loads(request.httprequest.data)

        gold = request.env["gold.price"].sudo().search([
            ("symbol", "=", data.get("symbol"))
        ], limit=1)

        if not gold:
            return http.Response(
                json.dumps({
                    "status": 404,
                    "message": "Data tidak ditemukan"
                }),
                content_type="application/json",
                status=404
            )

        gold.write({
            "name": data.get("name"),
            "price": data.get("price"),
            "currency": data.get("currency"),
            "updated_at": data.get("updated_at"),
        })

        return http.Response(
            json.dumps({
                "status": 200,
                "message": "Data berhasil diupdate",
                "data" : data
            }),
            content_type="application/json",
            status=200
        )

# delete api
    @http.route(
    ['/api/gold_price_delete/'],
    type='http',
    auth='public',
    methods=['DELETE'],
    csrf=False
    )
    def gold_price_delete(self, **params):

        data = json.loads(request.httprequest.data)

        gold = request.env["gold.price"].sudo().search([
            ("name", "=", data.get("name"))
        ], limit=1)

        if not gold:
            return http.Response(
                json.dumps({
                    "status": 404,
                    "message": "Data tidak ditemukan"
                }),
                content_type="application/json",
                status=404
            )

        gold.unlink()

        return http.Response(
            json.dumps({
                "status": 200,
                "message": "Data berhasil dihapus"
            }),
            content_type="application/json",
            status=200
        )
