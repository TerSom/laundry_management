from odoo import models, fields

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'sequence ,name'

    name = fields.Char(required=True)
    property_ids = fields.One2many('estate.property', 'type_id',)
    sequence = fields.Integer('Sequence', default=1)
    
    _sql_constraints = [
        ('check_unique_name', 'UNIQUE(name)',
        'Nama harus unik')
    ]