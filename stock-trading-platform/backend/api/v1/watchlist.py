from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from database import get_db
from models import User, Stock, WatchList
from core.security import verify_token
from comprehensive_indian_stocks import mock_provider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])
security = HTTPBearer()


@router.get("")
async def get_watchlist(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        watchlist_items = db.query(WatchList).filter(WatchList.user_id == user.id).all()
        result = []
        for item in watchlist_items:
            stock = db.query(Stock).filter(Stock.id == item.stock_id).first()
            if stock:
                price_data = mock_provider.get_current_price(stock.symbol)
                result.append({"id": item.id, "stock_id": stock.id, "symbol": stock.symbol, "name": stock.name, "current_price": price_data.get("current_price", 0), "change": price_data.get("change", 0), "change_percent": price_data.get("change_percent", 0), "market_cap": price_data.get("market_cap", 0), "pe_ratio": price_data.get("pe_ratio", 0)})
        return {"watchlist": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch watchlist")


@router.post("")
async def add_to_watchlist(payload: Dict[str, str], credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        symbol = payload.get("symbol")
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            stock_data = mock_provider.get_current_price(symbol)
            stock = Stock(symbol=symbol, name=stock_data.get("name", symbol), exchange=stock_data.get("exchange", "NSE"), sector=stock_data.get("sector", "Unknown"), market_cap=stock_data.get("market_cap", 0))
            db.add(stock)
            db.commit()
            db.refresh(stock)
        existing = db.query(WatchList).filter(WatchList.user_id == user.id, WatchList.stock_id == stock.id).first()
        if existing:
            return {"message": "Stock already in watchlist", "id": existing.id}
        new_item = WatchList(user_id=user.id, stock_id=stock.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return {"message": "Added to watchlist", "id": new_item.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")


@router.delete("/{id}")
async def remove_from_watchlist(id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        item = db.query(WatchList).filter(WatchList.id == id, WatchList.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
        db.delete(item)
        db.commit()
        return {"message": "Removed from watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove from watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist")
