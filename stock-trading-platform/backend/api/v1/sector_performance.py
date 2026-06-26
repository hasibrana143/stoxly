import random
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Query

from comprehensive_indian_stocks import mock_provider

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/sectors", tags=["Sector Performance"])


def _compute_sector_data(all_stocks):
    sectors = {}
    for s in all_stocks:
        sec = s.get("sector", "Unknown")
        if sec not in sectors:
            sectors[sec] = {"stocks": [], "market_cap": 0}
        sectors[sec]["stocks"].append(s)
        sectors[sec]["market_cap"] += s.get("market_cap", 0) or 0
    return sectors


@router.get("/performance")
async def get_sector_performance():
    """
    Get performance for all sectors.
    Returns: [{sector, stocks_count, market_cap, change_1d, change_1w, change_1m, change_3m, change_1y, avg_pe, avg_roe}]
    """
    try:
        all_stocks = mock_provider.get_all_stocks()
        sectors = _compute_sector_data(all_stocks)
        result = []
        for sec, data in sectors.items():
            stocks = data["stocks"]
            count = len(stocks)
            avg_pe = sum(s.get("pe_ratio", 0) or 0 for s in stocks) / count if count else 0
            avg_roe = sum(s.get("roe", 0) or 0 for s in stocks) / count if count else 0
            avg_change_1d = sum(s.get("change_percent", 0) or 0 for s in stocks) / count if count else 0
            avg_change_1w = sum(s.get("price_change_1w", 0) or 0 for s in stocks) / count if count else 0
            avg_change_1m = sum(s.get("price_change_1m", 0) or 0 for s in stocks) / count if count else 0
            avg_change_3m = sum(s.get("price_change_3m", 0) or 0 for s in stocks) / count if count else 0
            avg_change_1y = sum(s.get("price_change_1y", 0) or 0 for s in stocks) / count if count else 0
            result.append({
                "sector": sec,
                "stocks_count": count,
                "market_cap": round(data["market_cap"], 2),
                "change_1d": round(avg_change_1d, 2),
                "change_1w": round(avg_change_1w, 2),
                "change_1m": round(avg_change_1m, 2),
                "change_3m": round(avg_change_3m, 2),
                "change_1y": round(avg_change_1y, 2),
                "avg_pe": round(avg_pe, 2),
                "avg_roe": round(avg_roe, 2),
            })
        result.sort(key=lambda x: abs(x["change_1d"]), reverse=True)
        return {"sectors": result}
    except Exception as e:
        logger.error(f"Sector performance error: {str(e)}")
        return {"sectors": []}


@router.get("/{sector}/stocks")
async def get_sector_stocks(sector: str):
    """Get all stocks in a sector"""
    try:
        all_stocks = mock_provider.get_all_stocks()
        filtered = [s for s in all_stocks if s.get("sector", "").lower() == sector.lower()]
        if not filtered:
            all_sectors = sorted(set(s.get("sector", "Unknown") for s in all_stocks))
            return {"sector": sector, "stocks": [], "available_sectors": all_sectors}
        avg_change = sum(s.get("change_percent", 0) or 0 for s in filtered) / len(filtered)
        return {"sector": sector, "total_stocks": len(filtered), "avg_change_percent": round(avg_change, 2), "stocks": filtered}
    except Exception as e:
        logger.error(f"Sector stocks error for {sector}: {str(e)}")
        return {"sector": sector, "stocks": []}


@router.get("/heatmap")
async def get_sector_heatmap():
    """
    Returns data for a treemap/heatmap visualization.
    [{sector, market_cap, change_percent, color, stocks: [{symbol, name, market_cap, change_percent}]}]
    """
    try:
        all_stocks = mock_provider.get_all_stocks()
        sectors = _compute_sector_data(all_stocks)
        result = []
        for sec, data in sectors.items():
            stocks = data["stocks"]
            avg_change = sum(s.get("change_percent", 0) or 0 for s in stocks) / len(stocks) if stocks else 0
            color = "green" if avg_change > 0 else "red" if avg_change < 0 else "gray"
            stock_items = [
                {
                    "symbol": s["symbol"],
                    "name": s["name"],
                    "market_cap": s.get("market_cap", 0) or 0,
                    "change_percent": s.get("change_percent", 0) or 0,
                }
                for s in stocks
            ]
            stock_items.sort(key=lambda x: abs(x["change_percent"]), reverse=True)
            result.append({
                "sector": sec,
                "market_cap": round(data["market_cap"], 2),
                "change_percent": round(avg_change, 2),
                "color": color,
                "stocks": stock_items,
            })
        result.sort(key=lambda x: x["market_cap"], reverse=True)
        return {"heatmap": result}
    except Exception as e:
        logger.error(f"Sector heatmap error: {str(e)}")
        return {"heatmap": []}


@router.get("/top-movers")
async def get_top_movers(
    type: str = Query("gainers", regex="^(gainers|losers|active)$"),
    sector: Optional[str] = None,
    limit: int = 10,
):
    """
    Get top gainers, losers, or most active stocks.
    Can filter by sector.
    """
    try:
        all_stocks = mock_provider.get_all_stocks()
        if sector:
            all_stocks = [s for s in all_stocks if s.get("sector", "").lower() == sector.lower()]
        if type == "gainers":
            sorted_stocks = sorted(all_stocks, key=lambda x: x.get("change_percent", 0) or 0, reverse=True)
        elif type == "losers":
            sorted_stocks = sorted(all_stocks, key=lambda x: x.get("change_percent", 0) or 0)
        else:
            sorted_stocks = sorted(all_stocks, key=lambda x: x.get("volume", 0) or 0, reverse=True)
        top = sorted_stocks[:limit]
        return {
            "type": type,
            "sector": sector,
            "count": len(top),
            "stocks": [
                {
                    "symbol": s["symbol"],
                    "name": s["name"],
                    "current_price": s.get("current_price"),
                    "change_percent": s.get("change_percent"),
                    "volume": s.get("volume"),
                    "market_cap": s.get("market_cap"),
                }
                for s in top
            ],
        }
    except Exception as e:
        logger.error(f"Top movers error: {str(e)}")
        return {"type": type, "sector": sector, "stocks": []}
