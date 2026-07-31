from odoo import fields,models
from odoo.exceptions import ValidationError
from urllib.parse import quote

class AccountMove(models.Model):
    _inherit = 'account.move'

    laundry_order_id = fields.Many2one('laundry.order')
    def action_send_whatsapp(self): 
        self.ensure_one()
    
        phone = self.laundry_order_id.partner_id.mobile or self.partner_id.phone
    
        if not phone: 
            raise ValidationError("Customer has no phone number.")
        # bersihkan nomor 
        phone = phone.replace("+", "").replace(" ", "")

        order_name = self.laundry_order_id.name or '-'
    
        message = (
            f"Yth. {self.partner_id.name},%0A%0A"
            f"Dengan ini kami informasikan bahwa pesanan laundry Anda dengan nomor *{order_name}* "
            f"telah selesai dan *siap untuk diambil*.%0A%0A"
            f"Rincian Pembayaran:%0A"
            f"Total: *Rp {self.amount_total:,.0f}*%0A%0A"
            f"Kami tunggu kedatangan Anda. Terima kasih atas kepercayaannya. 🙏"
        )

        url = f"https://wa.me/{phone}?text={message}"

        return { 
            'type': 'ir.actions.act_url', 
            'url': url, 
            'target': 'new', 
        }