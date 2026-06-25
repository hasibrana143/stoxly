from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import (
    User, UserProfile, NotificationSettings, DisplayPreferences, 
    UserActivity, Subscription, LoginHistory
)
from profile_schemas import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    NotificationSettingsCreate, NotificationSettingsUpdate, NotificationSettingsResponse,
    DisplayPreferencesCreate, DisplayPreferencesUpdate, DisplayPreferencesResponse,
    UserActivityResponse, SubscriptionResponse, LoginHistoryResponse
)
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(prefix="/api/profile", tags=["Profile"])
security = HTTPBearer()

# --- Basic Info ---
@router.get("/basic", response_model=UserProfileResponse)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        # Return empty/default profile if not exists
        return UserProfileResponse(
            id=0, user_id=user.id, full_name="", phone_number="", 
            date_of_birth=None, address="", city="", country="", 
            bio="", avatar_url="", created_at=datetime.now(), updated_at=datetime.now()
        )
    return profile

@router.put("/basic", response_model=UserProfileResponse)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        # Create new
        profile = UserProfile(user_id=user.id, **profile_data.dict(exclude_unset=True))
        db.add(profile)
    else:
        # Update existing
        for key, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

# --- Notification Settings ---
@router.get("/notifications", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    settings = db.query(NotificationSettings).filter(NotificationSettings.user_id == user.id).first()
    if not settings:
        # Create default settings
        settings = NotificationSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/notifications", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    settings_data: NotificationSettingsUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    settings = db.query(NotificationSettings).filter(NotificationSettings.user_id == user.id).first()
    if not settings:
        settings = NotificationSettings(user_id=user.id, **settings_data.dict(exclude_unset=True))
        db.add(settings)
    else:
        for key, value in settings_data.dict(exclude_unset=True).items():
            setattr(settings, key, value)
            
    db.commit()
    db.refresh(settings)
    return settings

# --- Display Preferences ---
@router.get("/display", response_model=DisplayPreferencesResponse)
async def get_display_preferences(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    prefs = db.query(DisplayPreferences).filter(DisplayPreferences.user_id == user.id).first()
    if not prefs:
        prefs = DisplayPreferences(user_id=user.id)
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs

@router.put("/display", response_model=DisplayPreferencesResponse)
async def update_display_preferences(
    prefs_data: DisplayPreferencesUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    prefs = db.query(DisplayPreferences).filter(DisplayPreferences.user_id == user.id).first()
    if not prefs:
        prefs = DisplayPreferences(user_id=user.id, **prefs_data.dict(exclude_unset=True))
        db.add(prefs)
    else:
        for key, value in prefs_data.dict(exclude_unset=True).items():
            setattr(prefs, key, value)
            
    db.commit()
    db.refresh(prefs)
    return prefs

# --- Activity & Stats ---
@router.get("/activity", response_model=List[UserActivityResponse])
async def get_user_activity(
    limit: int = 20,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    activities = db.query(UserActivity).filter(UserActivity.user_id == user.id)\
        .order_by(UserActivity.created_at.desc()).limit(limit).all()
    return activities

@router.get("/login-history", response_model=List[LoginHistoryResponse])
async def get_login_history(
    limit: int = 10,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    history = db.query(LoginHistory).filter(LoginHistory.user_id == user.id)\
        .order_by(LoginHistory.login_time.desc()).limit(limit).all()
    return history

# --- Subscription ---
@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user_email = verify_token(credentials.credentials)
    user = db.query(User).filter(User.email == user_email).first()
    
    sub = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not sub:
        # Return a default "Free" subscription object (not saved to DB yet)
        return SubscriptionResponse(
            id=0, user_id=user.id, plan_name="Free", plan_type="free",
            price=0.0, status="active", start_date=datetime.now(), 
            next_billing_date=None, created_at=datetime.now(), updated_at=datetime.now()
        )
    return sub
