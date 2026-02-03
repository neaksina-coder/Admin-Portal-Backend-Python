# utils/email.py
import smtplib
from email.message import EmailMessage


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    smtp_use_tls: bool,
    from_email: str,
    to_email: str,
    subject: str,
    content: str,
    html_content: str | None = None,
):
    message = EmailMessage()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)
    if html_content:
        message.add_alternative(html_content, subtype="html")

    if smtp_use_tls:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
    else:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(message)
