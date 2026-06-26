from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from profile_schemas import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    NotificationSettingsCreate, NotificationSettingsUpdate, NotificationSettingsResponse,
    DisplayPreferencesCreate, DisplayPreferencesUpdate, DisplayPreferencesResponse,
    UserActivityResponse, SubscriptionResponse, LoginHistoryResponse
)
from core.security import verify_token
from repositories.profile_repository import (
    UserProfileRepository, NotificationSettingsRepository, DisplayPreferencesRepository,
    UserActivityRepository, SubscriptionRepository, LoginHistoryRepository,
)
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])
security = HTTPBearer()


def _get_user(credentials: HTTPAuthorizationCredentials, db: Session):
    user_email = verify_token(credentials.credentials)
    user = UserRepository(db).get_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/basic", response_model=UserProfileResponse)
async def get_user_profile(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = UserProfileRepository(db)
    profile = repo.get_by_user_id(user.id)
    if not profile:
        return UserProfileResponse(id=0, user_id=user.id, full_name="", phone_number="", date_of_birth=None, address="", city="", country="", bio="", avatar_url="", created_at=datetime.now(), updated_at=datetime.now())
    return profile


@router.put("/basic", response_model=UserProfileResponse)
async def update_user_profile(profile_data: UserProfileUpdate, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = UserProfileRepository(db)
    profile = repo.get_by_user_id(user.id)
    if not profile:
        profile = repo.create(user.id, **profile_data.dict(exclude_unset=True))
    else:
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
    return profile


@router.get("/notifications", response_model=NotificationSettingsResponse)
async def get_notification_settings(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = NotificationSettingsRepository(db)
    settings = repo.get_by_user_id(user.id)
    if not settings:
        settings = repo.create(user.id)
    return settings


@router.put("/notifications", response_model=NotificationSettingsResponse)
async def update_notification_settings(settings_data: NotificationSettingsUpdate, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = NotificationSettingsRepository(db)
    settings = repo.get_by_user_id(user.id)
    if not settings:
        settings = repo.create(user.id, **settings_data.dict(exclude_unset=True))
    else:
        for key, value in settings_data.dict(exclude_unset=True).items():
            setattr(settings, key, value)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("/display", response_model=DisplayPreferencesResponse)
async def get_display_preferences(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = DisplayPreferencesRepository(db)
    prefs = repo.get_by_user_id(user.id)
    if not prefs:
        prefs = repo.create(user.id)
    return prefs


@router.put("/display", response_model=DisplayPreferencesResponse)
async def update_display_preferences(prefs_data: DisplayPreferencesUpdate, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = DisplayPreferencesRepository(db)
    prefs = repo.get_by_user_id(user.id)
    if not prefs:
        prefs = repo.create(user.id, **prefs_data.dict(exclude_unset=True))
    else:
        for key, value in prefs_data.dict(exclude_unset=True).items():
            setattr(prefs, key, value)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.get("/activity", response_model=List[UserActivityResponse])
async def get_user_activity(limit: int = 20, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    return UserActivityRepository(db).get_by_user_id(user.id, limit)


@router.get("/login-history", response_model=List[LoginHistoryResponse])
async def get_login_history(limit: int = 10, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    return LoginHistoryRepository(db).get_by_user_id(user.id, limit)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    user = _get_user(credentials, db)
    repo = SubscriptionRepository(db)
    sub = repo.get_by_user_id(user.id)
    if not sub:
        return SubscriptionResponse(id=0, user_id=user.id, plan_name="Free", plan_type="free", price=0.0, status="active", start_date=datetime.now(), next_billing_date=None, created_at=datetime.now(), updated_at=datetime.now())
    return sub
