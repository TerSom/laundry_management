from odoo import fields,models,Command

class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        res = super().action_sold()

        self.env['account.move'].create({
            'partner_id' : self.buyer_id.id,
            'invoice_date' : self.create_date,
            'move_type' : 'out_invoice',
            'invoice_line_ids' : [
                Command.create({
                    'name' : 'Agency Commission (6%)',
                    'quantity' : 1,
                    'price_unit' : self.selling_price * 0.06
                }),
                Command.create({
                    'name' : 'Administrative Fees',
                    'quantity' : 1,
                    'price_unit' : 100.0
                })
            ]
        })

        return res
