from odoo import http
from odoo.http import request
import json


class LaundryApiController(http.Controller):

    @http.route('/api/orders', type='http', auth='public', methods=['GET'], csrf=False)
    def get_orders(self, **kwargs):
        try:
            orders = request.env['laundry.order'].sudo().search([], limit=10)

            data = []
            for order in orders:
                lines = []
                for line in order.line_ids:
                    lines.append({
                        'service' : line.service_id.name,
                        'quantity' : line.quantity,
                        'unit_price' : line.price_unit,
                        'subtotal' : line.subtotal,
                    })

                data.append({
                    'id': order.id,
                    'name': order.name,
                    'customer': order.partner_id.name,
                    'state': order.state,
                    'start_date': order.date_received.isoformat() if order.date_received else None,
                    'delivered_date': order.delivered_date.isoformat() if order.delivered_date else None,
                    'total_price': order.total_price,
                    'lines' : lines
                })

            return request.make_response(
                json.dumps(data),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'error': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

    @http.route('/api/orders/<int:order_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_order(self, order_id, **kwargs):
        order = request.env['laundry.order'].sudo().browse(order_id)

        if not order.exists(): 
            return request.make_response( 
                json.dumps({'error': 'Order not found'}), 
                headers=[('Content-Type', 'application/json')], 
                status=404
            )
        
        lines = []
        for line in order.line_ids:
            lines.append({
            'service' : line.service_id.name,
            'quantity' : line.quantity,
            'unit_price' : line.price_unit,
            'subtotal' : line.subtotal,
        })

        data = {
            'id': order.id,
            'name': order.name,
            'customer': order.partner_id.name,
            'state': order.state,
            'start_date': order.date_received.isoformat() if order.date_received else None,
            'delivered_date': order.delivered_date.isoformat() if order.delivered_date else None,
            'total_price': order.total_price,
            'lines' : lines
        }

        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')]
        )

    @http.route('/api/orders', type='json', auth='public', methods=['POST'], csrf=False) 
    def create_order(self, **kwargs):
        data = request.jsonrequest

        partner = request.env['res.partner'].sudo().browse(data.get('partner_id'))

        if not partner.exists(): 
            return {'error': 'Customer not found'}

        order = request.env['laundry.order'].sudo().create({
            'partner_id': partner.id, 
            'date_received': data.get('date_received'), 
            'state': 'received',
        })

        return { 'success': True, 
        'order_id': order.id, 
        'order_name': order.name, 
        }