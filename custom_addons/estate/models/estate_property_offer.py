from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import AccessError,UserError

class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Estater Property Offer'
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused')], copy=False , readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_id = fields.Many2one('estate.property', string='Property', required=True)
    validity = fields.Integer(string='Validity (days)', default=7)
    date_deadline = fields.Date(compute='_compute_date_deadline', inverse='_inverse_date_deadline')
    property_type_id = fields.Many2one('estate.property.type', related='property_id.estate_property_type_id' ,store=True)

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:

            create_date = (
                record.create_date.date()
                if record.create_date
                else fields.Date.today()
            )

            record.date_deadline = (
                create_date +
                timedelta(days=record.validity)
            )
    
    def _inverse_date_deadline(self):
        for record in self:

            create_date = (
                record.create_date.date()
                if record.create_date
                else fields.Date.today()
            )

            record.validity = (
                record.date_deadline -
                create_date
            ).days

    def action_accept(self):
        for record in self:
            if record.status == 'refused':
                raise AccessError("sudah refused tidak bisa accepted")
            else:
                record.property_id.selling_price = record.price
                record.property_id.buyer_id = record.partner_id
                record.property_id.state = "offer_accepted"
                record.status = 'accepted'
    
    def action_refuse(self):
        for record in self:
            if record.status == 'accepted':
                raise AccessError("sudah accepted tidak bisa refused")
            else:
                record.status = 'refused'
    
    _sql_constraints = [
        ('Check_price', 'CHECK(price >= 0)',
        'Price tidak boleh minus')
    ]

    @api.model_create_multi
    def create(self,vals_list):
        for vals in vals_list:
            property = self.env["estate.property"].browse(vals["property_id"])

            if property.offer_ids:
                
                highest_price = max(property.offer_ids.mapped("price"))

                if vals["price"] <= highest_price:
                    raise UserError(
                        "price harus lebih tinggii dari harga tertinggi di offer"
                    )

            property.state = 'offer_received'
        
        return super().create(vals_list)
