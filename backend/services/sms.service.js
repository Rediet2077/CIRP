/**
 * SMS via the Brevo transactional SMS API (same BREVO_API_KEY as email).
 * Brevo SMS needs purchased credits, so it is only attempted when
 * SMS_ENABLED=true; otherwise sending is reported as "skipped".
 */
class SmsService {
  isEnabled() {
    return Boolean(process.env.BREVO_API_KEY) && process.env.SMS_ENABLED === 'true';
  }

  /** "+251 91 123 4567" / "0911234567" -> "251911234567" */
  normalizePhone(phone) {
    let digits = String(phone || '').replace(/\D/g, '');
    if (digits.startsWith('00')) digits = digits.slice(2);
    if (digits.length === 10 && digits.startsWith('0')) digits = `251${digits.slice(1)}`;
    return digits;
  }

  async send(to, content) {
    const recipient = this.normalizePhone(to);
    if (recipient.length < 10) {
      throw new Error('Invalid phone number');
    }
    const response = await fetch('https://api.brevo.com/v3/transactionalSMS/sms', {
      method: 'POST',
      headers: {
        'api-key': process.env.BREVO_API_KEY,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        sender: (process.env.SMS_SENDER || 'CIRP').slice(0, 11),
        recipient,
        content,
        type: 'transactional',
      }),
      signal: AbortSignal.timeout(15000),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(data.message || `Brevo SMS error ${response.status}`);
    }
    return data;
  }
}

module.exports = new SmsService();
