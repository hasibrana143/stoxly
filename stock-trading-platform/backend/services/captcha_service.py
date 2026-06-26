import httpx
import logging

from core.config import settings

logger = logging.getLogger(__name__)

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_recaptcha(token: str | None) -> bool:
    if not settings.RECAPTCHA_SECRET_KEY or not settings.RECAPTCHA_SITE_KEY:
        return True
    if not token:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(RECAPTCHA_VERIFY_URL, data={"secret": settings.RECAPTCHA_SECRET_KEY, "response": token})
            result = resp.json()
            return result.get("success", False)
    except Exception as e:
        logger.warning(f"reCAPTCHA verification failed: {e}")
        return False
