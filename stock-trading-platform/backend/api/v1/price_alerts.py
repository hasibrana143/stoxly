from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from core.security import verify_token
from database import get_db
from sqlalchemy.orm import Session
from models import PriceAlert
from repositories.user_repository import UserRepository

router = APIRouter(prefix="/api/v1/alerts", tags=["Price Alerts"])
security = HTTPBearer()


def _normalize_symbol(s: str) -> str:
    return s.replace('.NS', '').replace('.BO', '').replace('.BSE', '')


class AlertCreate(BaseModel):
    symbol: str
    target_price: float
    condition: str = "above"
    note: Optional[str] = None


class AlertUpdate(BaseModel):
    target_price: Optional[float] = None
    condition: Optional[str] = None
    active: Optional[bool] = None
    note: Optional[str] = None


@router.post("/")
async def create_alert(
    alert: AlertCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        db_alert = PriceAlert(
            user_id=user.id,
            symbol=alert.symbol.upper(),
            target_price=alert.target_price,
            condition=alert.condition,
            note=alert.note,
        )
        db.add(db_alert)
        db.commit()
        db.refresh(db_alert)
        return {"message": "Alert created", "alert": db_alert}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create alert")


@router.get("/")
async def get_alerts(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        alerts = db.query(PriceAlert).filter(PriceAlert.user_id == user.id).all()
        return {"alerts": alerts}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")


@router.get("/{alert_id}")
async def get_alert(
    alert_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        alert = db.query(PriceAlert).filter(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == user.id,
        ).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return {"alert": alert}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch alert")


@router.put("/{alert_id}")
async def update_alert(
    alert_id: int,
    update: AlertUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        alert = db.query(PriceAlert).filter(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == user.id,
        ).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        update_data = update.dict(exclude_none=True)
        for key, value in update_data.items():
            setattr(alert, key, value)
        db.commit()
        db.refresh(alert)
        return {"message": "Alert updated", "alert": alert}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update alert")


@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        alert = db.query(PriceAlert).filter(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == user.id,
        ).first()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        db.delete(alert)
        db.commit()
        return {"message": "Alert deleted", "alert": alert}
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete alert")


@router.post("/check")
async def check_alerts(db: Session = Depends(get_db)):
    from comprehensive_indian_stocks import mock_provider

    triggered = []
    now = datetime.utcnow()
    alerts = db.query(PriceAlert).filter(
        PriceAlert.active == True,
        PriceAlert.triggered == False,
    ).all()
    for alert in alerts:
        try:
            price_data = mock_provider.get_current_price(_normalize_symbol(alert.symbol))
            current_price = price_data.get("current_price", 0)
            target = alert.target_price
            if (alert.condition == "above" and current_price >= target) or \
               (alert.condition == "below" and current_price <= target):
                alert.triggered = True
                alert.triggered_at = now
                triggered.append({
                    "alert_id": alert.id,
                    "user_id": alert.user_id,
                    "symbol": alert.symbol,
                    "target_price": target,
                    "current_price": current_price,
                    "condition": alert.condition,
                })
        except Exception as e:
            continue
    db.commit()
    return {"triggered": triggered, "checked_at": now.isoformat()}
