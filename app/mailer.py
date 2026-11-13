# Signed: ASDHEM | AMXME Web Solutions
"""Outgoing email via SMTP. Configure SMTP_* variables in .env."""
import logging
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr, make_msgid

log = logging.getLogger(__name__)


def smtp_configured():
    return bool(os.environ.get("SMTP_HOST"))


def send_mail(to, subject, body, reply_to=None, from_name="AMXME Website", attachments=None):
    """attachments: list of (filename, bytes, mime_type) – ASDHEM | used for invoices."""
    host = os.environ.get("SMTP_HOST")
    if not host:
        return False, "SMTP is not configured"
    port = int(os.environ.get("SMTP_PORT", "587"))
    security = os.environ.get("SMTP_SECURITY", "starttls").lower()  # starttls | ssl | none
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASSWORD", "")
    sender = os.environ.get("SMTP_FROM") or user

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = formataddr((from_name, sender))
    msg["To"] = to
    msg["Message-ID"] = make_msgid(domain=sender.split("@")[-1] if "@" in sender else None)
    if reply_to:
        msg["Reply-To"] = reply_to
    msg.set_content(body)
    for name, data, mime in attachments or ():
        maintype, _, subtype = mime.partition("/")
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=name)

    try:
        if security == "ssl":
            server = smtplib.SMTP_SSL(host, port, timeout=20)
        else:
            server = smtplib.SMTP(host, port, timeout=20)
            if security == "starttls":
                server.starttls()
        with server:
            if user:
                server.login(user, password)
            server.send_message(msg)
        return True, ""
    except Exception as e:  # noqa: BLE001
        log.exception("Sending mail failed")
        return False, str(e)
