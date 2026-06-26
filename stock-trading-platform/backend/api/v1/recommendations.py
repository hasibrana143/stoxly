from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
import logging

from database import get_db
from models import User, InvestmentProfile as DBInvestmentProfile
from services.ai_service import generate_stock_recommendations
from core.security import verify_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Recommendations"])
security = HTTPBearer()


@router.get("/recommendations")
async def get_user_recommendations(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        user_profile = db.query(DBInvestmentProfile).filter(DBInvestmentProfile.user_id == user.id).first()
        if not user_profile:
            return {"message": "Please create an investment profile to get personalized recommendations"}
        recommendations = generate_stock_recommendations(user_profile)
        return {"recommendations": recommendations, "profile": {"risk_level": user_profile.risk_level, "timeline": user_profile.timeline, "investment_amount": user_profile.investment_amount}}
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")
