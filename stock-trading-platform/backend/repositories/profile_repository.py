from sqlalchemy.orm import Session
from models import (
    UserProfile, NotificationSettings, DisplayPreferences,
    UserActivity, Subscription, LoginHistory, InvestmentProfile,
    InvestmentPreferences
)


class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> UserProfile | None:
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create(self, user_id: int, **kwargs) -> UserProfile:
        profile = UserProfile(user_id=user_id, **kwargs)
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: UserProfile, **kwargs) -> UserProfile:
        for field, value in kwargs.items():
            setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile


class NotificationSettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> NotificationSettings | None:
        return self.db.query(NotificationSettings).filter(
            NotificationSettings.user_id == user_id
        ).first()

    def create(self, user_id: int, **kwargs) -> NotificationSettings:
        settings = NotificationSettings(user_id=user_id, **kwargs)
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update(self, settings: NotificationSettings, **kwargs) -> NotificationSettings:
        for field, value in kwargs.items():
            setattr(settings, field, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings


class DisplayPreferencesRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> DisplayPreferences | None:
        return self.db.query(DisplayPreferences).filter(
            DisplayPreferences.user_id == user_id
        ).first()

    def create(self, user_id: int, **kwargs) -> DisplayPreferences:
        prefs = DisplayPreferences(user_id=user_id, **kwargs)
        self.db.add(prefs)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    def update(self, prefs: DisplayPreferences, **kwargs) -> DisplayPreferences:
        for field, value in kwargs.items():
            setattr(prefs, field, value)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs


class UserActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int, limit: int = 20) -> list[UserActivity]:
        return self.db.query(UserActivity).filter(
            UserActivity.user_id == user_id
        ).order_by(UserActivity.created_at.desc()).limit(limit).all()

    def create(self, user_id: int, **kwargs) -> UserActivity:
        activity = UserActivity(user_id=user_id, **kwargs)
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def update(self, activity: UserActivity, **kwargs) -> UserActivity:
        for field, value in kwargs.items():
            setattr(activity, field, value)
        self.db.commit()
        self.db.refresh(activity)
        return activity


class SubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> Subscription | None:
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id
        ).first()

    def create(self, user_id: int, **kwargs) -> Subscription:
        sub = Subscription(user_id=user_id, **kwargs)
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def update(self, sub: Subscription, **kwargs) -> Subscription:
        for field, value in kwargs.items():
            setattr(sub, field, value)
        self.db.commit()
        self.db.refresh(sub)
        return sub


class LoginHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int, limit: int = 10) -> list[LoginHistory]:
        return self.db.query(LoginHistory).filter(
            LoginHistory.user_id == user_id
        ).order_by(LoginHistory.login_time.desc()).limit(limit).all()

    def create(self, user_id: int, **kwargs) -> LoginHistory:
        entry = LoginHistory(user_id=user_id, **kwargs)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry


class InvestmentProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> InvestmentProfile | None:
        return self.db.query(InvestmentProfile).filter(
            InvestmentProfile.user_id == user_id
        ).first()

    def create(self, user_id: int, investment_amount: float, risk_level: str,
               timeline: str, **kwargs) -> InvestmentProfile:
        profile = InvestmentProfile(
            user_id=user_id, investment_amount=investment_amount,
            risk_level=risk_level, timeline=timeline, **kwargs
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: InvestmentProfile, **kwargs) -> InvestmentProfile:
        for field, value in kwargs.items():
            setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile


class InvestmentPreferencesRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: int) -> InvestmentPreferences | None:
        return self.db.query(InvestmentPreferences).filter(
            InvestmentPreferences.user_id == user_id
        ).first()

    def create(self, user_id: int, **kwargs) -> InvestmentPreferences:
        prefs = InvestmentPreferences(user_id=user_id, **kwargs)
        self.db.add(prefs)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    def update(self, prefs: InvestmentPreferences, **kwargs) -> InvestmentPreferences:
        for field, value in kwargs.items():
            setattr(prefs, field, value)
        self.db.commit()
        self.db.refresh(prefs)
        return prefs
