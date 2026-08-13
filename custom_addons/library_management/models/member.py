from odoo import models, fields, api

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'

    _inherits = {'res.partner' : 'partner_id'}

    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    memeber_number = fields.Char(string='Member Number', required=True, unique=True)
    registration_date = fields.Date(string='Registration Date', default=fields.Date.context_today)
