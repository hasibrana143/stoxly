from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
import random

from database import get_db
from core.security import verify_token
from repositories.portfolio_repository import PortfolioRepository
from repositories.watchlist_repository import WatchListRepository
from repositories.user_repository import UserRepository
from comprehensive_indian_stocks import mock_provider
from stock_data_list import INDIAN_STOCKS_DATABASE
from models import UserActivity, LoginHistory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])
security = HTTPBearer()


def _normalize_symbol(s: str) -> str:
    return s.replace('.NS', '').replace('.BO', '').replace('.BSE', '')


def _get_user(credentials: HTTPAuthorizationCredentials, db: Session):
    user_email = verify_token(credentials.credentials)
    user = UserRepository(db).get_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _compute_market_snapshot():
    nifty_stocks = [s for s in INDIAN_STOCKS_DATABASE if s.get("is_nifty50")]
    sensex_count = 30
    sensex_stocks = nifty_stocks[:sensex_count] if len(nifty_stocks) >= sensex_count else nifty_stocks

    advances = 0
    declines = 0
    unchanged = 0
    nifty_total = 0.0
    sensex_total = 0.0
    top_gainer = None
    top_loser = None
    most_active = None

    for s in nifty_stocks:
        try:
            price_data = mock_provider.get_current_price(_normalize_symbol(s["symbol"]))
            cp = price_data.get("current_price", 0)
            chg = price_data.get("change_percent", 0)
            vol = price_data.get("volume", 0)
            nifty_total += cp

            if chg > 0:
                advances += 1
            elif chg < 0:
                declines += 1
            else:
                unchanged += 1

            if top_gainer is None or chg > top_gainer["change_pct"]:
                top_gainer = {"symbol": s["symbol"], "name": s["name"], "change_pct": chg}
            if top_loser is None or chg < top_loser["change_pct"]:
                top_loser = {"symbol": s["symbol"], "name": s["name"], "change_pct": chg}
            if most_active is None or (vol or 0) > (most_active.get("volume") or 0):
                most_active = {"symbol": s["symbol"], "name": s["name"], "volume": vol}
        except Exception:
            continue

    for s in sensex_stocks:
        try:
            price_data = mock_provider.get_current_price(_normalize_symbol(s["symbol"]))
            sensex_total += price_data.get("current_price", 0)
        except Exception:
            continue

    nifty_level = round(nifty_total / max(len(nifty_stocks), 1), 2)
    sensex_level = round(sensex_total / max(len(sensex_stocks), 1), 2)

    return {
        "nifty": nifty_level,
        "sensex": sensex_level,
        "advances": advances,
        "declines": declines,
        "unchanged": unchanged,
        "top_gainer": top_gainer or {"symbol": "", "name": "", "change_pct": 0},
        "top_loser": top_loser or {"symbol": "", "name": "", "change_pct": 0},
        "most_active": most_active or {"symbol": "", "name": "", "volume": 0},
    }


@router.get("/summary")
async def get_dashboard_summary(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolios = PortfolioRepository(db).get_by_user_id(user.id)
        watchlist_items = WatchListRepository(db).get_by_user_id(user.id)

        total_investment = 0.0
        total_value = 0.0
        today_pnl = 0.0
        all_holdings = []

        for portfolio in portfolios:
            for holding in portfolio.holdings:
                try:
                    price_data = mock_provider.get_current_price(_normalize_symbol(holding.symbol))
                    current_price = price_data["current_price"]
                    name = price_data.get("name", holding.symbol)
                    change_pct = price_data.get("change_percent", 0)
                except Exception:
                    current_price = holding.average_price
                    name = holding.symbol
                    change_pct = 0

                current_value = holding.quantity * current_price
                investment_value = holding.quantity * holding.average_price
                pnl = current_value - investment_value

                total_investment += investment_value
                total_value += current_value
                today_pnl += investment_value * (change_pct / 100) if change_pct != 0 else 0

                all_holdings.append({
                    "symbol": holding.symbol,
                    "name": name,
                    "value": current_value,
                    "investment": investment_value,
                    "pnl": pnl,
                    "pnl_pct": (pnl / investment_value * 100) if investment_value > 0 else 0,
                    "change_pct": change_pct,
                    "portfolio_id": portfolio.id,
                    "portfolio_name": portfolio.name,
                })

        total_pnl = total_value - total_investment
        total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0

        all_holdings.sort(key=lambda x: x["value"], reverse=True)
        top_holding = all_holdings[0] if all_holdings else None

        best_performer = max(all_holdings, key=lambda x: x["change_pct"]) if all_holdings else None
        worst_performer = min(all_holdings, key=lambda x: x["change_pct"]) if all_holdings else None

        market = _compute_market_snapshot()
        now = datetime.utcnow()
        market_status = "open" if 9 <= now.hour < 15 and now.weekday() < 5 else "closed"

        return {
            "portfolio_value": round(total_value, 2),
            "total_investment": round(total_investment, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "today_pnl": round(today_pnl, 2),
            "watchlist_count": len(watchlist_items),
            "portfolio_count": len(portfolios),
            "top_holding": {
                "symbol": top_holding["symbol"],
                "name": top_holding["name"],
                "value": round(top_holding["value"], 2),
                "pnl": round(top_holding["pnl"], 2),
            } if top_holding else None,
            "best_performer": {
                "symbol": best_performer["symbol"],
                "name": best_performer["name"],
                "change_pct": round(best_performer["change_pct"], 2),
            } if best_performer else None,
            "worst_performer": {
                "symbol": worst_performer["symbol"],
                "name": worst_performer["name"],
                "change_pct": round(worst_performer["change_pct"], 2),
            } if worst_performer else None,
            "market_status": market_status,
            "nifty_level": market["nifty"],
            "sensex_level": market["sensex"],
            "advance_decline": {
                "advances": market["advances"],
                "declines": market["declines"],
                "unchanged": market["unchanged"],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Dashboard summary error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard summary")


@router.get("/quick-stats")
async def get_quick_stats():
    try:
        market = _compute_market_snapshot()
        return {
            "nifty": market["nifty"],
            "sensex": market["sensex"],
            "bank_nifty": round(market["nifty"] * random.uniform(0.95, 1.05), 2),
            "top_gainer": market["top_gainer"],
            "top_loser": market["top_loser"],
            "most_active": market["most_active"],
            "advance_decline": {
                "advances": market["advances"],
                "declines": market["declines"],
                "unchanged": market["unchanged"],
            },
        }
    except Exception as e:
        logger.error(f"Quick stats error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch quick stats")


@router.get("/portfolio-summary/{portfolio_id}")
async def get_portfolio_summary(portfolio_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        total_value = 0.0
        total_investment = 0.0
        day_change = 0.0
        sector_map = {}
        holdings_data = []

        for holding in portfolio.holdings:
            try:
                price_data = mock_provider.get_current_price(_normalize_symbol(holding.symbol))
                current_price = price_data["current_price"]
                name = price_data.get("name", holding.symbol)
                change_pct = price_data.get("change_percent", 0)
                sector = price_data.get("sector", "Other")
            except Exception:
                current_price = holding.average_price
                name = holding.symbol
                change_pct = 0
                sector = "Other"

            current_value = holding.quantity * current_price
            investment_value = holding.quantity * holding.average_price
            pnl = current_value - investment_value

            total_value += current_value
            total_investment += investment_value
            day_change += investment_value * (change_pct / 100)
            sector_map[sector] = sector_map.get(sector, 0) + current_value

            holdings_data.append({
                "symbol": holding.symbol,
                "name": name,
                "quantity": holding.quantity,
                "avg_price": holding.average_price,
                "current_price": current_price,
                "value": current_value,
                "investment": investment_value,
                "pnl": pnl,
                "pnl_pct": (pnl / investment_value * 100) if investment_value > 0 else 0,
                "weight": 0,
                "change_pct": change_pct,
            })

        total_pnl = total_value - total_investment
        total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0

        for h in holdings_data:
            h["weight"] = round((h["value"] / total_value * 100), 2) if total_value > 0 else 0

        holdings_data.sort(key=lambda x: x["value"], reverse=True)
        top_holdings = holdings_data[:5]

        sector_exposure = [
            {"sector": s, "percentage": round((v / total_value * 100), 2) if total_value > 0 else 0}
            for s, v in sorted(sector_map.items(), key=lambda x: x[1], reverse=True)
        ]

        unique_stocks = len(holdings_data)
        max_concentration = max((h["weight"] for h in holdings_data), default=0)
        diversification_score = max(0, min(100, 100 - max_concentration + unique_stocks * 5))
        diversification_score = min(100, diversification_score)

        return {
            "total_value": round(total_value, 2),
            "total_investment": round(total_investment, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "day_change": round(day_change, 2),
            "day_change_pct": round((day_change / total_investment * 100), 2) if total_investment > 0 else 0,
            "sector_exposure": sector_exposure,
            "top_holdings": [
                {
                    "symbol": h["symbol"],
                    "name": h["name"],
                    "weight": h["weight"],
                    "pnl": round(h["pnl"], 2),
                }
                for h in top_holdings
            ],
            "diversification_score": round(diversification_score, 1),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio summary error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio summary")


@router.get("/recent-activity")
async def get_recent_activity(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)

        activity = []
        logins = db.query(LoginHistory).filter(
            LoginHistory.user_id == user.id
        ).order_by(LoginHistory.login_time.desc()).limit(5).all()

        for login in logins:
            ts = login.login_time.isoformat() if login.login_time else datetime.utcnow().isoformat()
            activity.append({
                "type": "login",
                "message": f"Logged in from {login.device_info or 'unknown device'}",
                "timestamp": ts,
                "icon": "login",
            })

        portfolios = PortfolioRepository(db).get_by_user_id(user.id)
        for portfolio in portfolios:
            for holding in portfolio.holdings:
                if holding.created_at:
                    activity.append({
                        "type": "holding_added",
                        "message": f"Added {holding.symbol} to {portfolio.name}",
                        "timestamp": holding.created_at.isoformat(),
                        "icon": "add_circle",
                    })

        watchlist_items = WatchListRepository(db).get_by_user_id(user.id)
        for item in watchlist_items:
            if item.created_at:
                activity.append({
                    "type": "watchlist",
                    "message": f"Added stock to watchlist",
                    "timestamp": item.created_at.isoformat(),
                    "icon": "visibility",
                })

        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        return activity[:20]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recent activity error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch recent activity")
