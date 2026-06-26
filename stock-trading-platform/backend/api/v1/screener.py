from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
import logging

from database import get_db
from models import User, UserScreenerFilter
from schemas import ScreenerFilters
from core.security import verify_token
from screener_service import screener_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/screener", tags=["Screener"])
security = HTTPBearer()


@router.post("/screen")
async def screen_stocks(filters: ScreenerFilters):
    try:
        return screener_service.screen_stocks(filters)
    except Exception as e:
        logger.error(f"Screening error: {str(e)}")
        raise HTTPException(status_code=500, detail="Screening failed")


@router.get("/sectors")
async def get_sector_analysis():
    try:
        return {"sectors": screener_service.get_sector_analysis()}
    except Exception as e:
        logger.error(f"Sector analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sector analysis")


@router.get("/peers/{symbol}")
async def get_peer_comparison(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        peer_data = screener_service.get_peer_comparison(clean_symbol)
        if not peer_data:
            raise HTTPException(status_code=404, detail="Stock not found")
        return peer_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Peer comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch peer comparison")


@router.get("/top/{criteria}")
async def get_top_stocks(criteria: str, limit: int = 20):
    valid_criteria = ["market_cap", "gainers_1d", "losers_1d", "volume", "screener_score", "dividend_yield"]
    if criteria not in valid_criteria:
        raise HTTPException(status_code=400, detail=f"Invalid criteria. Must be one of: {valid_criteria}")
    try:
        return {"criteria": criteria, "stocks": screener_service.get_top_stocks(criteria, min(limit, 50))}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Top stocks error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch top stocks")


@router.get("/quarters/{symbol}")
async def get_quarters(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        return {"symbol": clean_symbol, "quarters": screener_service.get_quarterly_results(clean_symbol)}
    except Exception as e:
        logger.error(f"Quarterly results error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch quarterly results")


@router.get("/financials/pl/{symbol}")
async def get_profit_loss(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        return {"symbol": clean_symbol, "profit_loss": screener_service.get_profit_loss(clean_symbol)}
    except Exception as e:
        logger.error(f"P&L error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch P&L")


@router.get("/financials/balance/{symbol}")
async def get_balance_sheet(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        return {"symbol": clean_symbol, "balance_sheet": screener_service.get_balance_sheet(clean_symbol)}
    except Exception as e:
        logger.error(f"Balance sheet error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch balance sheet")


@router.get("/financials/cashflow/{symbol}")
async def get_cash_flow(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        return {"symbol": clean_symbol, "cash_flow": screener_service.get_cash_flow(clean_symbol)}
    except Exception as e:
        logger.error(f"Cash flow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cash flow")


@router.get("/stock/{symbol}")
async def get_screener_stock_details(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        details = screener_service.get_stock_details(clean_symbol)
        if not details:
            raise HTTPException(status_code=404, detail="Stock not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screener details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details")


@router.get("/filters/presets")
async def get_filter_presets():
    return {"presets": {
        "value_stocks": {"name": "Value Stocks", "description": "Undervalued stocks with low P/E and P/B ratios", "filters": {"pe_ratio_max": 15, "pb_ratio_max": 2, "roe_min": 15, "debt_to_equity_max": 1, "sort_by": "pe_ratio", "sort_order": "asc"}},
        "growth_stocks": {"name": "Growth Stocks", "description": "High growth companies with strong revenue and profit growth", "filters": {"revenue_growth_1y_min": 15, "profit_growth_1y_min": 20, "roe_min": 15, "sort_by": "revenue_growth_1y", "sort_order": "desc"}},
        "dividend_stocks": {"name": "Dividend Stocks", "description": "High dividend yielding stocks", "filters": {"dividend_yield_min": 3, "debt_to_equity_max": 1.5, "current_ratio_min": 1, "sort_by": "dividend_yield", "sort_order": "desc"}},
        "quality_stocks": {"name": "Quality Stocks", "description": "High quality companies with strong financials", "filters": {"roe_min": 20, "debt_to_equity_max": 0.5, "current_ratio_min": 1.5, "net_margin_min": 10, "sort_by": "screener_score", "sort_order": "desc"}},
        "nifty50": {"name": "Nifty 50 Stocks", "description": "All Nifty 50 index stocks", "filters": {"only_nifty50": True, "sort_by": "market_cap", "sort_order": "desc"}},
        "small_cap_gems": {"name": "Small Cap Gems", "description": "High potential small cap stocks", "filters": {"market_cap_category": ["small"], "roe_min": 15, "revenue_growth_1y_min": 10, "debt_to_equity_max": 1, "sort_by": "screener_score", "sort_order": "desc"}}
    }}


@router.get("/filters/list")
async def list_user_filters(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        filters = db.query(UserScreenerFilter).filter(UserScreenerFilter.user_id == user.id).order_by(UserScreenerFilter.id.desc()).all()
        return {"filters": [{"id": f.id, "filter_name": f.filter_name, "filter_criteria": f.filter_criteria, "is_default": f.is_default} for f in filters]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List filters error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list filters")


@router.post("/filters/save")
async def save_user_filter(payload: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        name = payload.get("filter_name")
        criteria = payload.get("filter_criteria")
        if not name or criteria is None:
            raise HTTPException(status_code=400, detail="Missing filter_name or filter_criteria")
        user_filter = UserScreenerFilter(user_id=user.id, filter_name=name, filter_criteria=json.dumps(criteria))
        db.add(user_filter)
        db.commit()
        filters = db.query(UserScreenerFilter).filter(UserScreenerFilter.user_id == user.id).order_by(UserScreenerFilter.id.desc()).all()
        return {"filters": [{"id": f.id, "filter_name": f.filter_name, "filter_criteria": f.filter_criteria, "is_default": f.is_default} for f in filters]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save filter error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save filter")


@router.delete("/filters/{filter_id}")
async def delete_user_filter(filter_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        filt = db.query(UserScreenerFilter).filter(UserScreenerFilter.id == filter_id, UserScreenerFilter.user_id == user.id).first()
        if not filt:
            raise HTTPException(status_code=404, detail="Filter not found")
        db.delete(filt)
        db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete filter error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete filter")
