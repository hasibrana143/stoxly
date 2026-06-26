from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta, date
import calendar

router = APIRouter(prefix="/api/v1/ipos", tags=["IPO Calendar"])

_UPCOMING_IPOS = [
    {"symbol": "TATATECH", "name": "Tata Technologies", "price_range": "450-500", "open_date": "2024-11-20", "close_date": "2024-11-23", "listing_date": "2024-11-28", "lot_size": 30, "min_investment": 15000, "listing_gains": None, "status": "upcoming"},
    {"symbol": "IRFC", "name": "Indian Railway Finance Corp", "price_range": "250-260", "open_date": "2024-12-05", "close_date": "2024-12-08", "listing_date": "2024-12-12", "lot_size": 60, "min_investment": 15600, "listing_gains": None, "status": "upcoming"},
    {"symbol": "MAMATA", "name": "Mamata Machinery", "price_range": "220-245", "open_date": "2024-12-16", "close_date": "2024-12-19", "listing_date": "2024-12-24", "lot_size": 50, "min_investment": 12250, "listing_gains": None, "status": "upcoming"},
    {"symbol": "DAMCAP", "name": "Dam Capital Advisors", "price_range": "280-300", "open_date": "2024-12-18", "close_date": "2024-12-21", "listing_date": "2024-12-27", "lot_size": 45, "min_investment": 13500, "listing_gains": None, "status": "upcoming"},
    {"symbol": "UNIHEALTH", "name": "Unihealth Hospitals", "price_range": "350-380", "open_date": "2025-01-08", "close_date": "2025-01-11", "listing_date": "2025-01-17", "lot_size": 35, "min_investment": 13300, "listing_gains": None, "status": "upcoming"},
    {"symbol": "GFLTD", "name": "Green Energy Ltd", "price_range": "190-210", "open_date": "2025-01-15", "close_date": "2025-01-18", "listing_date": "2025-01-23", "lot_size": 70, "min_investment": 14700, "listing_gains": None, "status": "upcoming"},
    {"symbol": "NATFOODS", "name": "Natural Foods Ltd", "price_range": "160-175", "open_date": "2025-01-22", "close_date": "2025-01-25", "listing_date": "2025-01-30", "lot_size": 80, "min_investment": 14000, "listing_gains": None, "status": "upcoming"},
    {"symbol": "DIGIBANK", "name": "Digital Bank of India", "price_range": "400-440", "open_date": "2025-02-05", "close_date": "2025-02-08", "listing_date": "2025-02-13", "lot_size": 30, "min_investment": 13200, "listing_gains": None, "status": "upcoming"},
    {"symbol": "SPACETECH", "name": "Space Technology India", "price_range": "520-570", "open_date": "2025-02-12", "close_date": "2025-02-15", "listing_date": "2025-02-20", "lot_size": 25, "min_investment": 14250, "listing_gains": None, "status": "upcoming"},
    {"symbol": "MEDIRIGHT", "name": "MediRight Pharma", "price_range": "140-155", "open_date": "2025-02-19", "close_date": "2025-02-22", "listing_date": "2025-02-27", "lot_size": 95, "min_investment": 14725, "listing_gains": None, "status": "upcoming"},
    {"symbol": "QUICKLOG", "name": "QuickLog Logistics", "price_range": "175-195", "open_date": "2025-03-05", "close_date": "2025-03-08", "listing_date": "2025-03-13", "lot_size": 65, "min_investment": 12675, "listing_gains": None, "status": "upcoming"},
]

_RECENT_IPOS = [
    {"symbol": "IDEA", "name": "Vodafone Idea FPO", "listing_date": "2024-10-15", "issue_price": 150, "listing_price": 168, "current_price": 185, "listing_gains": 12.0, "status": "listed"},
    {"symbol": "OYO", "name": "Oravel Stays (OYO)", "listing_date": "2024-10-22", "issue_price": 320, "listing_price": 355, "current_price": 340, "listing_gains": 10.9, "status": "listed"},
    {"symbol": "MNTN", "name": "Mountain Dew Beverages", "listing_date": "2024-09-30", "issue_price": 275, "listing_price": 298, "current_price": 312, "listing_gains": 8.4, "status": "listed"},
    {"symbol": "AQUAMAL", "name": "AquaMall Water Solutions", "listing_date": "2024-09-18", "issue_price": 185, "listing_price": 210, "current_price": 228, "listing_gains": 13.5, "status": "listed"},
    {"symbol": "FINCAP", "name": "FinCapital Advisors", "listing_date": "2024-09-05", "issue_price": 420, "listing_price": 465, "current_price": 490, "listing_gains": 10.7, "status": "listed"},
    {"symbol": "EVOLVE", "name": "Evolve Mobility", "listing_date": "2024-08-20", "issue_price": 240, "listing_price": 285, "current_price": 310, "listing_gains": 18.8, "status": "listed"},
    {"symbol": "EDTECH", "name": "EduTech India", "listing_date": "2024-08-07", "issue_price": 360, "listing_price": 340, "current_price": 315, "listing_gains": -5.6, "status": "listed"},
    {"symbol": "HOMEFIR", "name": "HomeFirst Finance", "listing_date": "2024-07-24", "issue_price": 520, "listing_price": 550, "current_price": 575, "listing_gains": 5.8, "status": "listed"},
    {"symbol": "CLOUDSEC", "name": "CloudSecure Solutions", "listing_date": "2024-07-10", "issue_price": 195, "listing_price": 230, "current_price": 265, "listing_gains": 17.9, "status": "listed"},
    {"symbol": "AGROFR", "name": "AgroFresh Farms", "listing_date": "2024-06-26", "issue_price": 135, "listing_price": 150, "current_price": 160, "listing_gains": 11.1, "status": "listed"},
]


def _get_last_thursday(year: int, month: int) -> str:
    """Get the last Thursday of a given month (FO expiry day)."""
    last_day = calendar.monthrange(year, month)[1]
    last_date = date(year, month, last_day)
    offset = (last_date.weekday() - 3) % 7
    expiry = last_date - timedelta(days=offset)
    return expiry.isoformat()


def _get_weekly_expiry_dates(year: int, month: int) -> List[str]:
    """Get all Thursday dates in a month (weekly expiry)."""
    thursdays = []
    first_day = date(year, month, 1)
    weekday = first_day.weekday()
    days_until_thursday = (3 - weekday) % 7
    first_thursday = first_day + timedelta(days=days_until_thursday)
    current = first_thursday
    while current.month == month:
        thursdays.append(current.isoformat())
        current += timedelta(days=7)
    return thursdays


@router.get("/upcoming")
async def get_upcoming_ipos():
    """Get upcoming IPOs with subscription status"""
    return {
        "ipos": _UPCOMING_IPOS,
        "total": len(_UPCOMING_IPOS),
        "as_of": datetime.now().isoformat()
    }


@router.get("/recent")
async def get_recent_ipos(limit: int = Query(20, ge=1, le=50)):
    """Get recently listed IPOs with performance"""
    sorted_recent = sorted(_RECENT_IPOS, key=lambda x: x["listing_date"], reverse=True)
    return {
        "ipos": sorted_recent[:limit],
        "total": len(sorted_recent),
        "as_of": datetime.now().isoformat()
    }


@router.get("/calendar")
async def get_ipo_calendar(month: Optional[int] = Query(None, ge=1, le=12), year: Optional[int] = Query(None, ge=2020, le=2030)):
    """Get IPO calendar for a specific month/year"""
    now = datetime.now()
    month = month or now.month
    year = year or now.year

    combined = _UPCOMING_IPOS + _RECENT_IPOS
    filtered = []
    for ipo in combined:
        ld = ipo.get("listing_date") or ipo.get("close_date")
        if ld:
            dt = datetime.strptime(ld, "%Y-%m-%d")
            if dt.year == year and dt.month == month:
                filtered.append(ipo)

    return {
        "month": month,
        "year": year,
        "ipos": filtered,
        "count": len(filtered)
    }


@router.get("/fo-expiry")
async def get_fo_expiry():
    """
    Get monthly F&O expiry dates for the next 6 months.
    Returns: [{month, year, expiry_date, weekly_expiry_dates: []}]
    """
    now = datetime.now()
    result = []
    for i in range(6):
        m = (now.month + i - 1) % 12 + 1
        y = now.year + (now.month + i - 1) // 12
        result.append({
            "month": m,
            "year": y,
            "expiry_date": _get_last_thursday(y, m),
            "weekly_expiry_dates": _get_weekly_expiry_dates(y, m)
        })
    return {"expiry_calendar": result}


@router.get("/{symbol}")
async def get_ipo_detail(symbol: str):
    """Get detailed info about a specific IPO"""
    symbol = symbol.upper()
    for ipo in _UPCOMING_IPOS + _RECENT_IPOS:
        if ipo["symbol"] == symbol:
            return ipo
    return {"error": f"IPO with symbol '{symbol}' not found", "symbol": symbol}
