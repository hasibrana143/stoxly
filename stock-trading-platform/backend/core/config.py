import sys
from decouple import config
from typing import List, Optional


class Settings:
    APP_NAME: str = "Stoxly.ai API"
    VERSION: str = "1.0.0"
    DEBUG: bool = config('DEBUG', default=False, cast=bool)

    DATABASE_URL: str = config('DATABASE_URL', default='sqlite:///./stock_platform.db')
    REDIS_URL: str = config('REDIS_URL', default='redis://localhost:6379/0')

    SECRET_KEY: str = config('SECRET_KEY', default='')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config('ACCESS_TOKEN_EXPIRE_MINUTES', default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config('REFRESH_TOKEN_EXPIRE_DAYS', default=7, cast=int)

    PASSWORD_EXPIRY_DAYS: int = config('PASSWORD_EXPIRY_DAYS', default=90, cast=int)
    PASSWORD_HISTORY_COUNT: int = config('PASSWORD_HISTORY_COUNT', default=5, cast=int)

    CORS_ORIGINS: List[str] = config('CORS_ORIGINS', default='http://localhost:3000').split(',')

    GEMINI_API_KEY: Optional[str] = config('GEMINI_API_KEY', default=None)
    ALPHA_VANTAGE_API_KEY: Optional[str] = config('ALPHA_VANTAGE_API_KEY', default=None)
    SENTRY_DSN: Optional[str] = config('SENTRY_DSN', default=None)

    RECAPTCHA_SITE_KEY: Optional[str] = config('RECAPTCHA_SITE_KEY', default=None)
    RECAPTCHA_SECRET_KEY: Optional[str] = config('RECAPTCHA_SECRET_KEY', default=None)

    SMTP_HOST: Optional[str] = config('SMTP_HOST', default=None)
    SMTP_PORT: int = config('SMTP_PORT', default=587, cast=int)
    SMTP_USER: Optional[str] = config('SMTP_USER', default=None)
    SMTP_PASSWORD: Optional[str] = config('SMTP_PASSWORD', default=None)
    SMTP_FROM: Optional[str] = config('SMTP_FROM', default='noreply@stoxly.ai')

    SSL_CERT_PATH: Optional[str] = config('SSL_CERT_PATH', default=None)
    SSL_KEY_PATH: Optional[str] = config('SSL_KEY_PATH', default=None)


settings = Settings()

if not settings.SECRET_KEY or settings.SECRET_KEY in ('change-me-in-production', 'your-secret-key-here-change-in-production'):
    if not settings.DEBUG:
        print("FATAL: SECRET_KEY is not set. Set a strong SECRET_KEY in production.", file=sys.stderr)
        sys.exit(1)
