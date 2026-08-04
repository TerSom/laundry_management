from odoo import models,fields,api,Command
from odoo.exceptions import ValidationError
from datetime import timedelta
import secrets


class LaundryOrder(models.Model):
    _name = 'laundry.order'
    _description = 'Laundry Order'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string="Order Number", required=True, copy=False, readonly=True, default="New")
    partner_id = fields.Many2one('res.partner', string="Customer",required=True)
    date_received = fields.Date(string='Start Date',default=fields.Date.today)
    state = fields.Selection(
        selection=[
            ('draft','Draft'),
            ('received','Received'),
            ('washing','Washing'),
            ('drying','Drying'),
            ('ironing','Ironing'),
            ('ready','Ready'),
            ('delivered','Delivered')
        ],
        default='draft',
        string='Status'
    )
    line_ids = fields.One2many('laundry.order.line', 'order_id', string="Order Lines")
    total_price = fields.Float(
        compute="_compute_total"
    )
    order_count = fields.Integer(
        compute="_compute_order_count"
    )
    invoice_id = fields.Many2one('account.move', string="invoice", readonly=True, copy=False)
    invoice_count = fields.Integer(compute='_compute_invoice_count')
    delivered_date = fields.Datetime(readonly=False,string="Delivered Date")
    stock_picking_id = fields.Many2one("stock.picking" , string='Stock Picking', readonly=True,)
    picking_count = fields.Integer( compute='_compute_picking_count' )
    has_wash = fields.Boolean(compute='_compute_process')
    has_dry = fields.Boolean(compute='_compute_process')
    has_iron = fields.Boolean(compute='_compute_process')
    next_stage = fields.Char(compute='_compute_next_stage')
    access_token = fields.Char( string='Access Token', copy=False, readonly=True )

    @api.depends('state', 'has_wash', 'has_dry', 'has_iron')
    def _compute_next_stage(self):
        for order in self:
            if order.state == 'draft':
                order.next_stage = 'received'
            elif order.state == 'received':
                if order.has_wash:
                    order.next_stage = 'washing'
                elif order.has_dry:
                    order.next_stage = 'drying'
                elif order.has_iron:
                    order.next_stage = 'ironing'
                else:
                    order.next_stage = 'ready'
            elif order.state == 'washing':
                if order.has_dry:
                    order.next_stage = 'drying'
                elif order.has_iron:
                    order.next_stage = 'ironing'
                else:
                    order.next_stage = 'ready'
            elif order.state == 'drying':
                if order.has_iron:
                    order.next_stage = 'ironing'
                else:
                    order.next_stage = 'ready'
            elif order.state == 'ironing':
                order.next_stage = 'ready'
            elif order.state == 'ready':
                order.next_stage = 'delivered'
            else:
                order.next_stage = False
    
    @api.depends('partner_id')
    def _compute_order_count(self):
        for record in self:
            record.order_count = self.env['laundry.order'].search_count([
                ("partner_id", "=", record.partner_id.id)
            ])

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for record in self:
            record.total_price = sum(record.line_ids.mapped('subtotal'))

    @api.depends('line_ids.service_id')
    def _compute_process(self):
        for order in self:
            services = order.line_ids.mapped('service_id')

            order.has_wash = any(services.mapped('need_wash'))
            order.has_dry = any(services.mapped('need_dry'))
            order.has_iron = any(services.mapped('need_iron'))
    
    @api.constrains('line_ids')
    def _check_same_process(self):
        for order in self:
            services = order.line_ids.mapped('service_id')

            process_type = set()

            for service in services:
                process_type.add((
                    service.need_wash,
                    service.need_dry,
                    service.need_iron,
                ))
            
            if len(process_type) > 1:
                raise ValidationError(
                    "Please use services with the same process in one order."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env['ir.sequence'].next_by_code("laundry.order") or "New"

        records = super().create(vals_list)

        for rec in records:
            if not rec.access_token:
                rec.access_token = secrets.token_hex(16)

        return records

    def get_portal_url(self): 
        self.ensure_one() 

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url') 

        return ( 
            f"{base_url}/laundry/status/{self.name}?token={self.access_token}" 
        )

    def action_received(self):
        for record in self:
            record.state = "received"
            record._create_stock_picking()
    
    def _compute_picking_count(self): 
        for order in self: 
            order.picking_count = 1 if order.stock_picking_id else 0
    
    def _compute_invoice_count(self):
        for invoice in self:
            invoice.invoice_count = 1 if invoice.invoice_id else 0

    def action_washing(self):
        for record in self:
            record.state = 'washing'

    def action_drying(self):
        for record in self:
            record.state = 'drying'

    def action_ironing(self):
        for record in self:
            record.state = 'ironing'

    def action_ready(self):
        for record in self:
            record.state = 'ready'

    def action_delivered(self):
        for record in self:
            if not record.partner_id:
                raise ValidationError("Please select a customer first.")

            if not record.line_ids:
                raise ValidationError("Please add at least one service.")
            
            partner = record.partner_id

            if partner.is_laundry_member:
                point = int(record.total_price / 1000) 
                partner.laundry_point += point

            invoice_lines = []
            for line in record.line_ids:
                invoice_lines.append(
                    Command.create({
                        'name': line.service_id.name,
                        'quantity': line.quantity,
                        'price_unit': line.price_unit,
                    })
                )

            invoice = self.env['account.move'].create({
                'partner_id': record.partner_id.id,
                'invoice_date': fields.Date.today(),
                'move_type': 'out_invoice',
                'invoice_line_ids': invoice_lines,
                'laundry_order_id': record.id,
            })

            record.invoice_id = invoice
            record.state = 'delivered'
            record.delivered_date = fields.Datetime.now()

        return {
            "type": "ir.actions.act_window",
            "name": "Customer Invoice",
            "res_model": "account.move",
            "res_id": invoice.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_view_customer_order(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Customer Orders",
            "res_model": "laundry.order",
            "view_mode": "list,form",
            "domain": [
            ("partner_id", "=", self.partner_id.id)
            ],
        }
    
    def action_view_invoice(self):
        self.ensure_one()

        return{
            "type" : "ir.actions.act_window",
            "name" : "Account Move",
            "res_model" : "account.move",
            "view_mode" : "form",
            "res_id" : self.invoice_id.id,
        }

    def action_send_email(self):
        self.ensure_one()

        template = self.env.ref(
            "laundry_management.email_template_laundry_ready"
        )

        template.send_mail(self.id, force_send=True)

    def cron_send_reminder(self):
        limit_date = fields.Datetime.now() - timedelta(days=3)

        orders = self.search([
            ("state", "=", "delivered"),
            ("delivered_date", "<=", limit_date),
        ])

        template = self.env.ref(
            "laundry_management.email_template_reminder"
        )

        for order in orders:
            template.send_mail(order.id, force_send=True)
    
    def action_view_picking(self): 
        self.ensure_one() 
        return { 
            'type': 'ir.actions.act_window', 
            'name': 'Stock Picking', 
            'res_model': 'stock.picking', 
            'view_mode': 'form', 
            'res_id': self.stock_picking_id.id, 
        }
    
    def _create_stock_picking(self):
        StockPicking = self.env['stock.picking'] 
        StockMove = self.env['stock.move']

        # ambil operation type internal transfer 
        picking_type = self.env.ref('stock.picking_type_internal')

        # lokasi sumber dan tujuan 
        source_location = self.env.ref('stock.stock_location_stock') 
        dest_location = self.env.ref('stock.stock_location_customers')

        picking = StockPicking.create({ 
            'partner_id': self.partner_id.id, 
            'picking_type_id': picking_type.id, 
            'location_id': source_location.id, 
            'location_dest_id': dest_location.id, 
            'origin': self.name, 
        })

        for line in self.line_ids:
            for product in line.service_id.consumable_product_ids:
                StockMove.create({ 
                    'name': product.name, 
                    'product_id': product.id, 
                    'product_uom_qty': line.quantity, 
                    'product_uom': product.uom_id.id, 
                    'picking_id': picking.id, 
                    'location_id': source_location.id, 
                    'location_dest_id': dest_location.id, 
                })
        
        self.stock_picking_id = picking.id
    
