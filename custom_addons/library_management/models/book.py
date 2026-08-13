from odoo import models,fields

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char(string='Title', required=True)
    isbn = fields.Char(string='ISBN')
    pages = fields.Integer(string='Number of Pages')
    active = fields.Boolean(string='Active', default=True)

    author_id = fields.Many2one('res.partner', string='Author', domain="[('is_company', '=', False)]")
    publisher_id = fields.Many2one('res.partner', string='Publisher', domain="[('is_company', '=', True)]")