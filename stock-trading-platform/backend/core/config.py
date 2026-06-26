from decouple import config
from typing import List

class Settings:
    APP_NAME: str = "Stoxly.ai API"
    VERSION: str = "1.0.0"
    DEBUG: bool = config('DEBUG', default=False, cast=bool)

    DATABASE_URL: str = config('DATABASE_URL', default='sqlite:///./stock_platform.db')

    SECRET_KEY: str = config('SECRET_KEY', default='change-me-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: List[str] = config('CORS_ORIGINS', default='http://localhost:3000').split(',')

    GEMINI_API_KEY: str | None = config('GEMINI_API_KEY', default=None)
    ALPHA_VANTAGE_API_KEY: str | None = config('ALPHA_VANTAGE_API_KEY', default=None)
    SENTRY_DSN: str | None = config('SENTRY_DSN', default=None)

settings = Settings()
