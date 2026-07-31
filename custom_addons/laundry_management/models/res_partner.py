from odoo import fields, models, api

class ResPartner(models.Model):
    _inherit = "res.partner"

    is_laundry_member = fields.Boolean(string='Laundry Member')
    member_code = fields.Char(string='Member Code', copy=False)
    laundry_point = fields.Integer(string='Laundry Point', default=0)

    total_spent = fields.Float( 
        string='Total Spent', 
        compute='_compute_total_spent', 
        store=True 
    )

    membership_level = fields.Selection([ 
        ('bronze', 'Bronze'), 
        ('silver', 'Silver'), 
        ('gold', 'Gold'), 
        ('platinum', 'Platinum'), 
    ], compute='_compute_membership_level', store=True)

    @api.depends("laundry_point")
    def _compute_membership_level(self):
        for partner in self:
            if partner.laundry_point >= 5000:
                partner.membership_level = 'platinum'
            elif partner.laundry_point >= 3000:
                partner.membership_level = 'gold'
            elif partner.laundry_point >= 1000:
                partner.membership_level = 'silver'
            else:
                partner.membership_level = 'bronze'

    @api.depends('laundry_point') 
    def _compute_total_spent(self): 
        for partner in self: 
            orders = self.env['laundry.order'].search([ 
                ('partner_id', '=', partner.id), 
                ('state', '=', 'delivered') 
            ]) 
            partner.total_spent = sum(orders.mapped('total_price'))
    
    @api.model 
    def create(self, vals): 
        if vals.get('is_laundry_member') and not vals.get('member_code'): 
            vals['member_code'] = self.env['ir.sequence'].next_by_code( 
                'laundry.member' 
            )
        return super().create(vals)