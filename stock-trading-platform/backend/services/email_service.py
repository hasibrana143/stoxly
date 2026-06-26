import logging
from pathlib import Path
from typing import Optional

from core.config import settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> bool:
    if not settings.SMTP_HOST or not settings.SMTP_USER:
        logger.info(f"[EMAIL DISABLED] Would send to {to}: {subject}")
        return False
    try:
        from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

        conf = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.SMTP_FROM or settings.SMTP_USER,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        message = MessageSchema(subject=subject, recipients=[to], body=body, subtype="html")
        fm = FastMail(conf)
        await fm.send_message(message)
        logger.info(f"Email sent to {to}: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        return False


async def send_verification_email(to: str, token: str) -> bool:
    verify_url = f"https://stoxly.ai/api/v1/auth/verify-email?token={token}"
    body = f"""
    <h2>Welcome to Stoxly.ai!</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <p><a href="{verify_url}">Verify Email Address</a></p>
    <p>If you did not create an account, please ignore this email.</p>
    <p>This link expires in 24 hours.</p>
    """
    return await send_email(to, "Verify your Stoxly.ai account", body)
