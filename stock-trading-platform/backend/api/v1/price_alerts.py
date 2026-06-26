from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import logging

from core.security import verify_token

router = APIRouter(prefix="/api/v1/alerts", tags=["Price Alerts"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

_alerts: Dict[str, list] = {}

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
async def create_alert(alert: AlertCreate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_email = verify_token(credentials.credentials)
        new_alert = {
            "id": str(uuid.uuid4()),
            "user_email": user_email,
            "symbol": alert.symbol.upper(),
            "target_price": alert.target_price,
            "condition": alert.condition,
            "active": True,
            "note": alert.note,
            "created_at": datetime.utcnow().isoformat(),
            "triggered_at": None,
            "triggered": False,
        }
        if user_email not in _alerts:
            _alerts[user_email] = []
        _alerts[user_email].append(new_alert)
        return {"message": "Alert created", "alert": new_alert}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create alert error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create alert")

@router.get("/")
async def get_alerts(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_email = verify_token(credentials.credentials)
        return {"alerts": _alerts.get(user_email, [])}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch alerts")

@router.get("/{alert_id}")
async def get_alert(alert_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_email = verify_token(credentials.credentials)
        user_alerts = _alerts.get(user_email, [])
        for a in user_alerts:
            if a["id"] == alert_id:
                return {"alert": a}
        raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get alert error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch alert")

@router.put("/{alert_id}")
async def update_alert(alert_id: str, update: AlertUpdate, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_email = verify_token(credentials.credentials)
        user_alerts = _alerts.get(user_email, [])
        for i, a in enumerate(user_alerts):
            if a["id"] == alert_id:
                update_data = update.dict(exclude_none=True)
                user_alerts[i].update(update_data)
                return {"message": "Alert updated", "alert": user_alerts[i]}
        raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update alert error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update alert")

@router.delete("/{alert_id}")
async def delete_alert(alert_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        user_email = verify_token(credentials.credentials)
        user_alerts = _alerts.get(user_email, [])
        for i, a in enumerate(user_alerts):
            if a["id"] == alert_id:
                removed = user_alerts.pop(i)
                return {"message": "Alert deleted", "alert": removed}
        raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete alert error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete alert")

@router.post("/check")
async def check_alerts():
    from comprehensive_indian_stocks import mock_provider
    triggered = []
    for user_email, user_alerts in _alerts.items():
        for alert in user_alerts:
            if not alert["active"] or alert["triggered"]:
                continue
            try:
                price_data = mock_provider.get_current_price(alert["symbol"])
                current_price = price_data.get("current_price", 0)
                target = alert["target_price"]
                if (alert["condition"] == "above" and current_price >= target) or \
                   (alert["condition"] == "below" and current_price <= target):
                    alert["triggered"] = True
                    alert["triggered_at"] = datetime.utcnow().isoformat()
                    triggered.append({
                        "alert_id": alert["id"],
                        "user_email": user_email,
                        "symbol": alert["symbol"],
                        "target_price": target,
                        "current_price": current_price,
                        "condition": alert["condition"],
                    })
            except Exception as e:
                logger.warning(f"Check alert error for {alert['symbol']}: {str(e)}")
                continue
    return {"triggered": triggered, "checked_at": datetime.utcnow().isoformat()}
