# utils/email_templates.py
from __future__ import annotations

import html
from typing import Optional


def _nl_to_br(text: str) -> str:
    return html.escape(text or "").replace("\n", "<br>")


def render_contact_reply_email(
    *,
    subject: str,
    reply_body: str,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    original_subject: Optional[str] = None,
    original_message: Optional[str] = None,
    business_name: str = "Sina Neak Business Tools",
    support_email: Optional[str] = None,
) -> str:
    safe_subject = html.escape(subject or "Reply to your inquiry")
    safe_name = html.escape(customer_name or "there")
    safe_business = html.escape(business_name)
    safe_reply = _nl_to_br(reply_body)
    safe_original_subject = html.escape(original_subject or "Your inquiry")
    safe_original_message = _nl_to_br(original_message or "")
    safe_customer_email = html.escape(customer_email or "")
    safe_support_email = html.escape(support_email or "")

    support_line = ""
    if safe_support_email:
        support_line = (
            f'For help, contact us at <a href="mailto:{safe_support_email}" '
            f'style="color:#2563eb;text-decoration:none;">{safe_support_email}</a>.'
        )

    original_section = ""
    if safe_original_message:
        original_section = f"""
            <tr>
              <td style="padding:20px 32px 0 32px;">
                <div style="font-size:13px;color:#64748b;margin-bottom:6px;">Original message</div>
                <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;padding:16px;color:#334155;font-size:14px;line-height:1.6;">
                  <div style="font-weight:600;color:#0f172a;margin-bottom:6px;">{safe_original_subject}</div>
                  <div>{safe_original_message}</div>
                </div>
              </td>
            </tr>
        """

    customer_line = ""
    if safe_customer_email:
        customer_line = f"<div style=\"color:#64748b;font-size:12px;\">Sent to {safe_customer_email}</div>"

    return f"""\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{safe_subject}</title>
  </head>
  <body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" cellpadding="0" cellspacing="0" width="100%" style="background:#f1f5f9;">
      <tr>
        <td align="center" style="padding:32px 16px;">
          <table role="presentation" cellpadding="0" cellspacing="0" width="640" style="max-width:640px;background:#ffffff;border-radius:16px;box-shadow:0 6px 18px rgba(15,23,42,0.12);overflow:hidden;">
            <tr>
              <td style="background:linear-gradient(135deg,#0ea5e9 0%,#2563eb 100%);padding:24px 32px;text-align:left;">
                <div style="color:#ffffff;font-size:16px;letter-spacing:0.4px;font-weight:600;">
                  {safe_business}
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:28px 32px 8px 32px;">
                <div style="font-size:20px;font-weight:700;color:#0f172a;line-height:1.3;">
                  {safe_subject}
                </div>
                <div style="font-size:14px;color:#64748b;margin-top:6px;">
                  Hi {safe_name},
                </div>
              </td>
            </tr>

            <tr>
              <td style="padding:8px 32px 24px 32px;color:#334155;font-size:15px;line-height:1.7;">
                {safe_reply}
              </td>
            </tr>

            {original_section}

            <tr>
              <td style="padding:24px 32px 32px 32px;">
                <div style="height:1px;background:#e2e8f0;margin-bottom:16px;"></div>
                <div style="color:#475569;font-size:13px;line-height:1.6;">
                  Thanks,<br>
                  {safe_business} Team
                </div>
                {customer_line}
              </td>
            </tr>

            <tr>
              <td style="background:#f8fafc;padding:20px 32px;border-top:1px solid #e2e8f0;">
                <div style="color:#94a3b8;font-size:12px;line-height:1.6;">
                  This email is a response to your contact inquiry.
                  {support_line}
                </div>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""
