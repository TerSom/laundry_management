import requests
import logging

from odoo import models, fields
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    laundry_order_id = fields.Many2one('laundry.order', string='Laundry Order')

    def _normalize_phone(self, phone):
        """Bersihkan dan normalize nomor telepon ke format 62xxxx untuk WhatsApp."""
        phone = phone.replace("+", "").replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "62" + phone[1:]
        elif not phone.startswith("62"):
            phone = "62" + phone
        return phone

    def action_send_whatsapp(self):
        self.ensure_one()

        ICP = self.env['ir.config_parameter'].sudo()
        waha_url = ICP.get_param('waha.url', 'http://127.0.0.1:3000')
        api_key = ICP.get_param('waha.api_key')

        if not api_key:
            raise ValidationError(
                "WAHA API Key belum dikonfigurasi. "
                "Silakan set parameter 'waha.api_key' di Settings > Technical > Parameters > System Parameters."
            )

        phone = (
            self.laundry_order_id.partner_id.mobile
            or self.laundry_order_id.partner_id.phone
            or self.partner_id.mobile
            or self.partner_id.phone
        )
        if not phone:
            raise ValidationError("Customer tidak memiliki nomor telepon.")

        phone = self._normalize_phone(phone)

        order_name = self.laundry_order_id.name or '-'
        message = (
            f"Yth. {self.partner_id.name},\n\n"
            f"Dengan ini kami informasikan bahwa pesanan laundry Anda dengan nomor *{order_name}* "
            f"telah selesai dan *sudah sampai*.\n\n"
            f"Rincian Pembayaran:\n"
            f"Total: *Rp {self.amount_total:,.0f}*\n\n"
            f"Terima kasih atas kepercayaannya."
        )

        url = f"{waha_url}/api/sendText"
        payload = {
            "session": "Default",
            "chatId": f"{phone}@c.us",
            "text": message,
        }
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
        except requests.exceptions.RequestException as e:
            _logger.error("WAHA connection error: %s", e)
            raise ValidationError(f"Tidak dapat terhubung ke server WAHA: {e}")

        if response.status_code not in (200, 201):
            _logger.error("WAHA send failed [%s]: %s", response.status_code, response.text)
            raise ValidationError(f"Gagal mengirim WhatsApp: {response.text}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'WhatsApp',
                'message': 'Pesan berhasil dikirim.',
                'type': 'success',
                'sticky': False,
            }
        }