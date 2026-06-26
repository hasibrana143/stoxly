from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import logging

from database import get_db
from schemas import InvestmentProfileCreate, InvestmentProfileUpdate, InvestmentProfile
from core.security import verify_token
from repositories.user_repository import UserRepository
from repositories.profile_repository import InvestmentProfileRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/profile", tags=["Profile"])


@router.post("/investment", response_model=InvestmentProfile)
async def create_investment_profile(profile: InvestmentProfileCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        existing_profile = InvestmentProfileRepository(db).get_by_user_id(user.id)
        if existing_profile:
            raise HTTPException(status_code=400, detail="Investment profile already exists")
        db_profile = InvestmentProfileRepository(db).create(
            user_id=user.id, investment_amount=profile.investment_amount,
            risk_level=profile.risk_level, timeline=profile.timeline,
            investment_goals=profile.investment_goals,
            monthly_income=profile.monthly_income, age=profile.age
        )
        return db_profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investment profile creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create investment profile")


@router.get("/investment", response_model=InvestmentProfile)
async def get_investment_profile(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        profile = InvestmentProfileRepository(db).get_by_user_id(user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Investment profile not found")
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investment profile fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investment profile")


@router.put("/investment", response_model=InvestmentProfile)
async def update_investment_profile(profile_update: InvestmentProfileUpdate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        profile = InvestmentProfileRepository(db).get_by_user_id(user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Investment profile not found")
        profile = InvestmentProfileRepository(db).update(profile, **profile_update.dict(exclude_unset=True))
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Investment profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update investment profile")
