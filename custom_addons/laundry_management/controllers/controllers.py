# -*- coding: utf-8 -*-
# from odoo import http


# class LaundryManagement(http.Controller):
#     @http.route('/laundry__management/laundry__management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/laundry__management/laundry__management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('laundry__management.listing', {
#             'root': '/laundry__management/laundry__management',
#             'objects': http.request.env['laundry__management.laundry__management'].search([]),
#         })

#     @http.route('/laundry__management/laundry__management/objects/<model("laundry__management.laundry__management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('laundry__management.object', {
#             'object': obj
#         })

