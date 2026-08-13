from odoo import models, fields, api
from datetime import timedelta

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Loan'

    name = fields.Char(string='No. Referensi', default='New', readonly=True)
    member_id = fields.Many2one('library.member', string='Member', required=True)
    book_id = fields.Many2one('library.book', string='Book', required=True)
    date_borrow = fields.Date(string='Borrow Date', default=fields.Date.context_today)
    date_return_expected = fields.Date(string='Expected Return Date', required=True)
    date_return_actual = fields.Date(string='Actual Return Date', readonly=True)
    currency_id = fields.Many2many('res.currency', string='Currency', defualt=lambda self: self.env.company.currency_id)


    state = fields.Selection([
        ('draft', 'Draft'),
        ('ongoing', 'Ongoing'),
        ('returned', 'Returned'),
    ], string='Status', default='draft')

    late_fee = fields.Monetary(string='Late Fee', compute='_compute_late_fee', store=True)

    @api.depends('date_borrow')
    def _onchange_date_borrow(self):
        for record in self:
            """Otomatis set tenggat waktu 7 hari dari tanggal pinjam"""
            if record.date_borrow:
                record.date_return_expected = record.date_borrow + timedelta(days=7)
    
    @api.depends('date_return_actual', 'date_return_expected')
    def _compute_late_fee(self):
        for record in self:
            """Menghitung denda jika tanggal kembali melebihi tenggat waktu"""
            fee = 0.0
            if record.date_return_actual and record.date_return_expected:
                if record.date_return_actual > record.date_return_expected:
                    delta = record.date_return_actual - record.date_return_expected
                    fee = delta.days * 5000.0

            record.late_fee = fee