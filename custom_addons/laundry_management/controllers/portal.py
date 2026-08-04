from odoo import http 
from odoo.http import request

class LaundryPortal(http.Controller):
    @http.route( '/laundry/status/<string:order_name>', type='http', auth='public', website=True )
    def laundry_status(self, order_name, token=None, **kw):
        order = request.env['laundry.order'].sudo().search([ ('name', '=', order_name) ], limit=1)

        if not order: 
            return request.not_found()

        # cek token 
        if not token or token != order.access_token: 
            return request.render( 'laundry_management.portal_access_denied')

        return request.render( 
            'laundry_management.portal_laundry_status', 
            { 
                'order': order 
            } 
        )