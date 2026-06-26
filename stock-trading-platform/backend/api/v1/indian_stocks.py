from fastapi import APIRouter, HTTPException
import logging

from schemas import IndianStockPrice
from comprehensive_indian_stocks import mock_provider, format_inr_price

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/indian-stocks", tags=["Indian Stocks"])


@router.get("/all")
async def get_all_indian_stocks():
    try:
        stocks_data = mock_provider.get_all_stocks()
        formatted_stocks = [{"symbol": s["symbol"], "name": s["name"], "sector": s["sector"], "market_cap_category": s["market_cap_category"], "current_price": s["current_price"], "formatted_price": format_inr_price(s["current_price"]), "change": s["change"], "change_percent": s["change_percent"], "is_nifty50": s["is_nifty50"], "is_nifty100": s["is_nifty100"], "volume": s["volume"], "market_cap": s["market_cap"]} for s in stocks_data]
        return {"stocks": formatted_stocks}
    except Exception as e:
        logger.error(f"Indian stocks fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Indian stocks")


@router.get("/price/{symbol}", response_model=IndianStockPrice)
async def get_indian_stock_price(symbol: str):
    try:
        clean_symbol = symbol.replace('.NS', '')
        price_data = mock_provider.get_current_price(clean_symbol)
        return IndianStockPrice(symbol=clean_symbol, current_price=price_data["current_price"], previous_close=price_data["previous_close"], change=price_data["change"], change_percent=price_data["change_percent"], volume=price_data["volume"], market_cap=price_data["market_cap"], company_name=price_data["name"], currency="INR", formatted_price=format_inr_price(price_data["current_price"]), pe_ratio=15.5, dividend_yield=0.02)
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Indian stock price fetch error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price")


@router.get("/search/{query}")
async def search_indian_stocks(query: str, limit: int = 20):
    try:
        return {"stocks": mock_provider.search_stocks(query, limit)}
    except Exception as e:
        logger.error(f"Indian stock search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Stock search failed")
