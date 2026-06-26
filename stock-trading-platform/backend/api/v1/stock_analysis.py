import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from comprehensive_indian_stocks import mock_provider
from core.security import verify_token
from database import get_db
from services.ai_analysis import analyze_stock, compare_stocks, generate_market_brief

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analysis", tags=["Stock Analysis"])
security = HTTPBearer()


def _normalize_symbol(s: str) -> str:
    return s.replace('.NS', '').replace('.BO', '').replace('.BSE', '')


@router.get("/stock/{symbol}")
async def analyze_stock_endpoint(
    symbol: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """AI-powered stock analysis with ratings, target price, support/resistance"""
    try:
        token_email = verify_token(credentials.credentials)
        stock = mock_provider.get_current_price(_normalize_symbol(symbol))
        fundamentals = {
            "pe_ratio": stock.get("pe_ratio"),
            "roe": stock.get("roe"),
            "roce": stock.get("roce"),
            "book_value": stock.get("book_value"),
            "dividend_yield": stock.get("dividend_yield"),
            "market_cap": stock.get("market_cap"),
            "sector": stock.get("sector"),
        }
        price_data = {
            "current_price": stock["current_price"],
            "previous_close": stock["previous_close"],
            "change": stock.get("change"),
            "change_percent": stock.get("change_percent"),
            "high_52w": stock.get("high_52w"),
            "low_52w": stock.get("low_52w"),
            "volume": stock.get("volume"),
            "price_change_1w": stock.get("price_change_1w"),
            "price_change_1m": stock.get("price_change_1m"),
            "price_change_3m": stock.get("price_change_3m"),
            "price_change_1y": stock.get("price_change_1y"),
        }
        result = await analyze_stock(symbol, stock["name"], price_data, fundamentals)
        return {
            "symbol": symbol,
            "name": stock["name"],
            **result,
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Stock analysis error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze stock")


@router.post("/compare")
async def compare_stocks_endpoint(
    symbols: List[str],
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Compare multiple stocks side by side"""
    try:
        token_email = verify_token(credentials.credentials)
        if len(symbols) > 5:
            raise HTTPException(status_code=400, detail="Maximum 5 symbols allowed for comparison")
        if len(symbols) < 2:
            raise HTTPException(status_code=400, detail="At least 2 symbols required for comparison")
        stocks = []
        for sym in symbols:
            try:
                stock = mock_provider.get_current_price(_normalize_symbol(sym))
                stocks.append(stock)
            except ValueError:
                raise HTTPException(status_code=404, detail=f"Stock not found: {sym}")
        comparison = await compare_stocks(stocks)
        return {"symbols": symbols, "comparison": comparison, "stocks": stocks}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to compare stocks")


@router.get("/market-brief")
async def get_market_brief_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """AI-generated daily market brief"""
    try:
        token_email = verify_token(credentials.credentials)
        all_stocks = mock_provider.get_all_stocks()
        sorted_gainers = sorted(all_stocks, key=lambda x: x.get("change_percent", 0), reverse=True)
        sorted_losers = sorted(all_stocks, key=lambda x: x.get("change_percent", 0))
        sectors = {}
        for s in all_stocks:
            sec = s.get("sector", "Unknown")
            if sec not in sectors:
                sectors[sec] = {"stocks": [], "total_change": 0, "count": 0}
            sectors[sec]["stocks"].append(s)
            sectors[sec]["total_change"] += s.get("change_percent", 0)
            sectors[sec]["count"] += 1
        sector_data = [
            {
                "sector": sec,
                "avg_change": round(data["total_change"] / data["count"], 2) if data["count"] else 0,
                "stock_count": data["count"],
            }
            for sec, data in sectors.items()
        ]
        market_data = {
            "advancers": len([s for s in all_stocks if s.get("change_percent", 0) > 0]),
            "decliners": len([s for s in all_stocks if s.get("change_percent", 0) < 0]),
            "unchanged": len([s for s in all_stocks if s.get("change_percent", 0) == 0]),
            "total_stocks": len(all_stocks),
        }
        brief = await generate_market_brief(market_data, sorted_gainers[:10], sorted_losers[:10], sector_data)
        return {
            "brief": brief,
            "market_summary": {
                "total_stocks": market_data["total_stocks"],
                "advancers": market_data["advancers"],
                "decliners": market_data["decliners"],
                "unchanged": market_data["unchanged"],
            },
            "top_gainers": [
                {"symbol": s["symbol"], "name": s["name"], "change_percent": s.get("change_percent")}
                for s in sorted_gainers[:5]
            ],
            "top_losers": [
                {"symbol": s["symbol"], "name": s["name"], "change_percent": s.get("change_percent")}
                for s in sorted_losers[:5]
            ],
        }
    except Exception as e:
        logger.error(f"Market brief error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate market brief")


@router.get("/news/{symbol}")
async def get_stock_news(symbol: str, limit: int = 10):
    """Get recent news for a stock (template-based for now)"""
    try:
        stock = mock_provider.get_current_price(_normalize_symbol(symbol))
        from datetime import datetime, timedelta
        sample_headlines = [
            {"headline": f"{stock['name']} reports strong quarterly earnings, beats estimates", "source": "Economic Times", "date": (datetime.now() - timedelta(days=1)).isoformat(), "url": f"https://economictimes.indiatimes.com/{symbol.lower()}"},
            {"headline": f"Analysts raise target price for {stock['name']} on growth outlook", "source": "Moneycontrol", "date": (datetime.now() - timedelta(days=2)).isoformat(), "url": f"https://www.moneycontrol.com/news/{symbol.lower()}"},
            {"headline": f"{stock['name']} expands operations, new manufacturing facility announced", "source": "Business Standard", "date": (datetime.now() - timedelta(days=3)).isoformat(), "url": f"https://www.business-standard.com/{symbol.lower()}"},
            {"headline": f"FIIs increase stake in {stock['name']} during the quarter", "source": "NDTV Profit", "date": (datetime.now() - timedelta(days=4)).isoformat(), "url": f"https://www.ndtvprofit.com/{symbol.lower()}"},
            {"headline": f"{stock['name']} board approves buyback proposal", "source": "Livemint", "date": (datetime.now() - timedelta(days=5)).isoformat(), "url": f"https://www.livemint.com/{symbol.lower()}"},
            {"headline": f"Sector tailwinds boost {stock['name']}'s near-term prospects", "source": "Economic Times", "date": (datetime.now() - timedelta(days=6)).isoformat(), "url": f"https://economictimes.indiatimes.com/{symbol.lower()}"},
            {"headline": f"Technical indicators suggest bullish momentum for {stock['name']}", "source": "Moneycontrol", "date": (datetime.now() - timedelta(days=7)).isoformat(), "url": f"https://www.moneycontrol.com/technical/{symbol.lower()}"},
            {"headline": f"{stock['name']} announces dividend of ₹5 per share", "source": "Business Standard", "date": (datetime.now() - timedelta(days=8)).isoformat(), "url": f"https://www.business-standard.com/dividend/{symbol.lower()}"},
            {"headline": f"Competition intensifies in {stock.get('sector', 'sector')} space, {stock['name']} holds ground", "source": "NDTV Profit", "date": (datetime.now() - timedelta(days=9)).isoformat(), "url": f"https://www.ndtvprofit.com/{symbol.lower()}"},
            {"headline": f"Q3 results preview: {stock['name']} expected to post double-digit growth", "source": "Livemint", "date": (datetime.now() - timedelta(days=10)).isoformat(), "url": f"https://www.livemint.com/results/{symbol.lower()}"},
        ]
        return {"symbol": symbol, "name": stock["name"], "total_articles": len(sample_headlines[:limit]), "articles": sample_headlines[:limit]}
    except ValueError:
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Stock news error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock news")
