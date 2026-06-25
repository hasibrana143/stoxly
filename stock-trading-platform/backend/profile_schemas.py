from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Enhanced Profile System Schemas

class UserProfileBase(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    location: Optional[str] = None
    preferred_language: str = "en"

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfile(UserProfileBase):
    id: int
    user_id: int
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class NotificationSettingsBase(BaseModel):
    price_alerts_enabled: bool = True
    price_alert_threshold: float = 5.0
    news_alerts_enabled: bool = True
    earnings_alerts_enabled: bool = True
    dividend_alerts_enabled: bool = True
    portfolio_updates_frequency: str = "daily"
    market_reminders_enabled: bool = False
    email_notifications: Optional[str] = None  # JSON string
    sms_notifications: Optional[str] = None  # JSON string
    push_notifications: Optional[str] = None  # JSON string

class NotificationSettingsCreate(NotificationSettingsBase):
    pass

class NotificationSettingsUpdate(NotificationSettingsBase):
    pass

class NotificationSettings(NotificationSettingsBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DisplayPreferencesBase(BaseModel):
    theme: str = "light"
    default_currency: str = "INR"
    number_format: str = "indian"
    date_format: str = "DD/MM/YYYY"
    chart_type: str = "candlestick"
    default_time_period: str = "1M"
    stocks_per_page: int = 25

class DisplayPreferencesCreate(DisplayPreferencesBase):
    pass

class DisplayPreferencesUpdate(DisplayPreferencesBase):
    pass

class DisplayPreferences(DisplayPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserSessionBase(BaseModel):
    device_info: Optional[str] = None
    browser: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None

class UserSession(UserSessionBase):
    id: int
    user_id: int
    session_token: str
    last_active: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginHistoryBase(BaseModel):
    ip_address: Optional[str] = None
    device_info: Optional[str] = None
    browser: Optional[str] = None
    location: Optional[str] = None
    success: bool = True

class LoginHistory(LoginHistoryBase):
    id: int
    user_id: int
    login_time: datetime
    
    class Config:
        from_attributes = True


class SubscriptionBase(BaseModel):
    plan_type: str = "free"
    status: str = "active"
    auto_renew: bool = False

class SubscriptionUpdate(BaseModel):
    plan_type: Optional[str] = None
    status: Optional[str] = None
    auto_renew: Optional[bool] = None

class Subscription(SubscriptionBase):
    id: int
    user_id: int
    start_date: datetime
    expiry_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PaymentHistoryBase(BaseModel):
    amount: float
    plan_type: str
    payment_method: Optional[str] = None
    status: str = "completed"

class PaymentHistory(PaymentHistoryBase):
    id: int
    user_id: int
    payment_date: datetime
    invoice_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserActivityBase(BaseModel):
    total_searches: int = 0
    most_viewed_stocks: Optional[str] = None  # JSON string
    recently_viewed_stocks: Optional[str] = None  # JSON string

class UserActivity(UserActivityBase):
    id: int
    user_id: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Password Change
class PasswordChange(BaseModel):
    current_password: str
    new_password: str

# Response type aliases for API endpoints
UserProfileResponse = UserProfile
NotificationSettingsResponse = NotificationSettings
DisplayPreferencesResponse = DisplayPreferences
UserActivityResponse = UserActivity
LoginHistoryResponse = LoginHistory
SubscriptionResponse = Subscription
