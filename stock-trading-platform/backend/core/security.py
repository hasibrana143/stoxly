from datetime import datetime, timedelta
import uuid
import bcrypt
from jose import jwt, JWTError
from fastapi import HTTPException, status

from core.config import settings
from core.session import is_token_blacklisted_by_jti


def _password_bytes(password: str) -> bytes:
    return password.encode('utf-8')


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_password_bytes(plain_password), _password_bytes(hashed_password))


def create_access_token(data: dict, expires_minutes: int | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": str(uuid.uuid4())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if is_token_blacklisted_by_jti(payload.get("jti")):
            raise HTTPException(status_code=401, detail="Token has been revoked")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
