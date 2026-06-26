from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import secrets
import uuid

from database import get_db
from schemas import UserCreate, UserLogin
from core.config import settings
from jose import jwt, JWTError
from core.security import create_access_token, get_password_hash, verify_password
from core.security_extras import brute_force_protection, validate_password, sanitize_input
from core.audit import audit_log
from core.session import blacklist_token
from repositories.user_repository import UserRepository
from services.totp_service import generate_totp_secret, get_totp_uri, generate_qr_code_base64, verify_totp
from services.captcha_service import verify_recaptcha
from services.email_service import send_verification_email
from models import User, PasswordHistory

logger = logging.getLogger("auth")
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
security = HTTPBearer()


@router.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    if not await verify_recaptcha(user.captcha_token):
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed")

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

    pw_history = PasswordHistory(user_id=db_user.id, hashed_password=hashed_password)
    db.add(pw_history)

    email_token = secrets.token_urlsafe(32)
    db_user.email_verification_token = email_token
    db.commit()

    await send_verification_email(db_user.email, email_token)

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_access_token(data={"sub": db_user.email, "type": "refresh"}, expires_minutes=1440)

    logger.info(f"User registered: {user.email}")
    audit_log("user.register", user=db_user.email)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}


@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = db.query(User).filter(User.email_verification_token == token, User.is_email_verified == False).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    user.is_email_verified = True
    user.email_verification_token = None
    db.commit()
    logger.info(f"Email verified: {user.email}")
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = UserRepository(db)
    user = repo.get_by_email(email)
    if not user or user.is_email_verified:
        raise HTTPException(status_code=400, detail="Email already verified or user not found")
    email_token = secrets.token_urlsafe(32)
    user.email_verification_token = email_token
    db.commit()
    await send_verification_email(user.email, email_token)
    return {"message": "Verification email resent"}


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    if not await verify_recaptcha(user.captcha_token):
        raise HTTPException(status_code=400, detail="CAPTCHA verification failed")

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
        audit_log("user.login", user=user.email, details={"success": False, "reason": "invalid_credentials"})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    brute_force_protection.reset(lock_key)

    if db_user.is_2fa_enabled and db_user.totp_secret:
        return {"require_2fa": True, "email": db_user.email, "message": "2FA code required"}

    if db_user.last_password_change:
        days_since_change = (datetime.utcnow() - db_user.last_password_change).days
        if days_since_change >= settings.PASSWORD_EXPIRY_DAYS:
            return {"password_expired": True, "email": db_user.email, "message": "Password expired. Please change your password."}

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_access_token(data={"sub": db_user.email, "type": "refresh"}, expires_minutes=1440)

    logger.info(f"User logged in: {user.email}")
    audit_log("user.login", user=user.email, details={"success": True})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}


@router.post("/login/2fa")
async def login_2fa(email: str = Body(...), code: str = Body(...), db: Session = Depends(get_db)):
    repo = UserRepository(db)
    db_user = repo.get_by_email(sanitize_input(email))
    if not db_user or not db_user.is_2fa_enabled or not db_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not enabled for this account")
    if not verify_totp(db_user.totp_secret, code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")

    access_token = create_access_token(data={"sub": db_user.email})
    refresh_token = create_access_token(data={"sub": db_user.email, "type": "refresh"}, expires_minutes=1440)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}


@router.post("/2fa/setup")
async def setup_2fa(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if payload.get("type") == "refresh":
            raise HTTPException(status_code=401, detail="Use access token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = UserRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.is_2fa_enabled:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    secret = generate_totp_secret()
    db_user.totp_secret = secret
    db.commit()
    qr_b64 = generate_qr_code_base64(secret, email)
    uri = get_totp_uri(secret, email)
    return {"secret": secret, "qr_code": qr_b64, "uri": uri, "message": "Scan QR with Google Authenticator, then call /2fa/verify with the code"}


@router.post("/2fa/verify")
async def verify_2fa(code: str = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = UserRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user or not db_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not set up")
    if not verify_totp(db_user.totp_secret, code):
        raise HTTPException(status_code=401, detail="Invalid 2FA code")
    db_user.is_2fa_enabled = True
    db.commit()
    backup_codes = [secrets.token_hex(4) for _ in range(5)]
    logger.info(f"2FA enabled: {email}")
    return {"message": "2FA enabled successfully", "backup_codes": backup_codes}


@router.post("/2fa/disable")
async def disable_2fa(password: str = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    repo = UserRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    db_user.is_2fa_enabled = False
    db_user.totp_secret = None
    db.commit()
    logger.info(f"2FA disabled: {email}")
    return {"message": "2FA disabled successfully"}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    blacklist_token(credentials.credentials)
    audit_log("user.logout", user="unknown")
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return {"message": "Not available without Redis"}


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


@router.post("/change-password")
async def change_password(old_password: str = Body(...), new_password: str = Body(...), credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    valid, msg = validate_password(new_password)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    repo = UserRepository(db)
    db_user = repo.get_by_email(email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(old_password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid current password")

    past_passwords = db.query(PasswordHistory).filter(PasswordHistory.user_id == db_user.id).order_by(PasswordHistory.created_at.desc()).limit(settings.PASSWORD_HISTORY_COUNT).all()
    for pw in past_passwords:
        if verify_password(new_password, pw.hashed_password):
            raise HTTPException(status_code=400, detail="Cannot reuse a recent password")

    new_hashed = get_password_hash(new_password)
    db_user.hashed_password = new_hashed
    db_user.last_password_change = datetime.utcnow()

    pw_entry = PasswordHistory(user_id=db_user.id, hashed_password=new_hashed)
    db.add(pw_entry)

    old_entries = db.query(PasswordHistory).filter(PasswordHistory.user_id == db_user.id).order_by(PasswordHistory.created_at.desc()).offset(settings.PASSWORD_HISTORY_COUNT).all()
    for entry in old_entries:
        db.delete(entry)

    db.commit()
    logger.info(f"Password changed: {email}")
    audit_log("user.password_change", user=email)
    return {"message": "Password changed successfully"}
