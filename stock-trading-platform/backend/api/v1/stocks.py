from fastapi import APIRouter, HTTPException
from typing import Dict, List
import logging

from schemas import MarketMover
from comprehensive_indian_stocks import mock_provider, format_inr_price
from screener_service import screener_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stocks", tags=["Stocks"])


@router.get("/search/{query}")
async def search_stocks(query: str):
    try:
        search_results = mock_provider.search_stocks(query, limit=20)
        return {"stocks": [{"symbol": s["symbol"], "name": s["name"], "exchange": s["exchange"], "sector": s["sector"], "market_cap_category": s["market_cap_category"]} for s in search_results]}
    except Exception as e:
        logger.error(f"Stock search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Stock search failed")


@router.get("/price/{symbol}")
async def get_stock_price(symbol: str):
    try:
        p = mock_provider.get_current_price(symbol)
        return {"symbol": p["symbol"], "current_price": p["current_price"], "previous_close": p["previous_close"], "change": p["change"], "change_percent": p["change_percent"], "volume": p["volume"], "market_cap": p["market_cap"], "company_name": p["name"]}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Price fetch error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price")


@router.get("/history/{symbol}")
async def get_stock_history(symbol: str, period: str = "1y", interval: str = "1d"):
    try:
        return {"symbol": symbol, "period": period, "interval": interval, "data": mock_provider.get_historical_data(symbol, period)}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"History fetch error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock history")


@router.get("/market-movers", response_model=Dict[str, List[MarketMover]])
async def get_market_movers(type: str = "gainers", limit: int = 10):
    try:
        all_stocks = mock_provider.get_all_stocks()
        sorted_stocks = sorted(all_stocks, key=lambda x: x["change_percent"], reverse=(type == "gainers"))
        return {"stocks": [{"rank": i + 1, "symbol": s["symbol"], "name": s["name"], "current_price": s["current_price"], "change_percent": s["change_percent"], "volume": s.get("volume", 0)} for i, s in enumerate(sorted_stocks[:limit])]}
    except Exception as e:
        logger.error(f"Market movers error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch market movers")


@router.get("/{symbol}")
async def get_stock_details_alias(symbol: str):
    try:
        try:
            p = mock_provider.get_current_price(symbol)
            return {"symbol": p["symbol"], "current_price": p["current_price"], "previous_close": p["previous_close"], "change": p["change"], "change_percent": p["change_percent"], "volume": p["volume"], "market_cap": p.get("market_cap", 0), "company_name": p["name"], "pe_ratio": p.get("pe_ratio", 0), "roe": p.get("roe", 0), "roce": p.get("roce", 0), "book_value": p.get("book_value", 0), "dividend_yield": p.get("dividend_yield", 0), "price_change_1w": p.get("price_change_1w", 0), "price_change_1m": p.get("price_change_1m", 0), "price_change_3m": p.get("price_change_3m", 0), "price_change_6m": p.get("price_change_6m", 0), "price_change_1y": p.get("price_change_1y", 0), "high_52w": p.get("high_52w", 0), "low_52w": p.get("low_52w", 0)}
        except ValueError:
            stock_details = screener_service.get_stock_details(symbol)
            if stock_details:
                return stock_details
            raise HTTPException(status_code=404, detail="Stock not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock details error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details")
