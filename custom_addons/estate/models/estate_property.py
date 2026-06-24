from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero
class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False, default=lambda self: fields.Date.today() + relativedelta(months=3))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    total_area = fields.Integer(compute='_compute_total_area')
    best_price = fields.Float(compute='_compute_best_price', store=True)
    garden_orientation = fields.Selection(
        [('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        string='Garden Orientation'
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        required=True,
        copy=False,
        default='new',
        readonly=True
    )
    estate_property_type_id = fields.Many2one('estate.property.type', string='Property Type')
    buyer_id = fields.Many2one('res.partner', string='Buyer', copy=False)
    salesperson_id = fields.Many2one('res.users', string='Salesperson', default=lambda self: self.env.user)
    tags_ids = fields.Many2many('estate.property.tag', string='Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')
    type_id = fields.Many2one('estate.property.type', 'property_ids')

    @api.depends('living_area','garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped('price')

            if prices:
                record.best_price = max(prices)
            else:
                record.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_sold(self):
        for record in self:
            if self.state == 'canceled':
                raise AccessError("status sudah cancel gk bisa di sold")
            elif self.state == 'sold':
                raise AccessError("status sudah sold")
            else:
                self.state = 'sold'

    def action_cancel(self):
        for record in self:
            if self.state == 'sold':
                raise AccessError("status sudah sold gk bisa di cancel")
            elif self.state == 'canceled':
                raise AccessError("status sudah cancel")
            else:
                self.state = 'canceled'

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price >= 0)',
         'Expected price tidak boleh minus')
    ]

    _sql_constraints = [
        ('check_selling_price', 'CHECK(selling_price >= 0)',
        'Selling price tidak boleh minus')
    ]

    @api.constrains('selling_price','expected_price')
    def _check_selling_price(self):
        for record in self:
            if float_is_zero(record.selling_price, precision_digits=2):
                continue
            
            if float_compare(record.selling_price,record.expected_price * 0.9, precision_digits=2) < 0:
                raise ValidationError(
                    "Selling price tidak boleh kurang dari 90% expected price"
                )