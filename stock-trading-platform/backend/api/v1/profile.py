from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import User, InvestmentProfile as DBInvestmentProfile
from schemas import InvestmentProfileCreate, InvestmentProfileUpdate, InvestmentProfile
from core.security import verify_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/profile", tags=["Profile"])
security = HTTPBearer()


@router.post("/investment", response_model=InvestmentProfile)
async def create_investment_profile(profile: InvestmentProfileCreate, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        existing_profile = db.query(DBInvestmentProfile).filter(DBInvestmentProfile.user_id == user.id).first()
        if existing_profile:
            raise HTTPException(status_code=400, detail="Investment profile already exists")
        db_profile = DBInvestmentProfile(user_id=user.id, investment_amount=profile.investment_amount, risk_level=profile.risk_level, timeline=profile.timeline, investment_goals=profile.investment_goals, monthly_income=profile.monthly_income, age=profile.age)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investment profile creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create investment profile")


@router.get("/investment", response_model=InvestmentProfile)
async def get_investment_profile(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        profile = db.query(DBInvestmentProfile).filter(DBInvestmentProfile.user_id == user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Investment profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investment profile fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investment profile")


@router.put("/investment", response_model=InvestmentProfile)
async def update_investment_profile(profile_update: InvestmentProfileUpdate, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        profile = db.query(DBInvestmentProfile).filter(DBInvestmentProfile.user_id == user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="Investment profile not found")
        for field, value in profile_update.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        db.commit()
        db.refresh(profile)
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investment profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update investment profile")
