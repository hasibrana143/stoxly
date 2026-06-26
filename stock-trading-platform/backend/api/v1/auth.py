from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from database import get_db
from schemas import UserCreate, UserLogin
from core.config import settings
from jose import jwt, JWTError
from core.security import create_access_token, get_password_hash, verify_password
from core.security_extras import brute_force_protection, validate_password, sanitize_input
from repositories.user_repository import UserRepository

logger = logging.getLogger("auth")
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
security = HTTPBearer()


@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    user.email = sanitize_input(user.email)
    user.username = sanitize_input(user.username)

    valid, msg = validate_password(user.password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    repo = UserRepository(db)
    if repo.get_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if repo.get_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    db_user = repo.create(user.username, user.email, hashed_password)
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_access_token(data={"sub": db_user.email, "type": "refresh"}, expires_minutes=1440)

    logger.info(f"User registered: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    user.email = sanitize_input(user.email)
    lock_key = f"login:{user.email}"

    locked, remaining = brute_force_protection.is_locked(lock_key)
    if locked:
        logger.warning(f"Brute force blocked: {user.email}")
        raise HTTPException(status_code=429, detail=f"Account locked. Try again in {remaining} seconds")

    repo = UserRepository(db)
    db_user = repo.get_by_email(user.email)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        brute_force_protection.record_attempt(lock_key, success=False)
        logger.warning(f"Failed login attempt: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    brute_force_protection.reset(lock_key)
    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_access_token(data={"sub": db_user.email, "type": "refresh"}, expires_minutes=1440)

    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        new_access = create_access_token(data={"sub": email})
        new_refresh = create_access_token(data={"sub": email, "type": "refresh"}, expires_minutes=1440)
        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
