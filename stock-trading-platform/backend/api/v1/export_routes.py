from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
import io
import logging
from datetime import datetime

from database import get_db
from core.security import verify_token
from repositories.portfolio_repository import PortfolioRepository, HoldingRepository
from repositories.watchlist_repository import WatchListRepository, StockRepository
from repositories.user_repository import UserRepository
from services.export_service import export_portfolio_csv, export_transactions_csv, export_watchlist_csv, export_report_json
from comprehensive_indian_stocks import mock_provider
from models import Transaction, Stock as StockModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/export", tags=["Export"])
security = HTTPBearer()


def _get_user(credentials: HTTPAuthorizationCredentials, db: Session):
    user_email = verify_token(credentials.credentials)
    user = UserRepository(db).get_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/portfolio/{portfolio_id}/csv")
async def export_portfolio_csv_endpoint(portfolio_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        holdings_data = []
        for holding in portfolio.holdings:
            try:
                price_data = mock_provider.get_current_price(holding.symbol)
                current_price = price_data["current_price"]
                name = price_data.get("name", holding.symbol)
            except Exception:
                current_price = holding.average_price
                name = holding.symbol

            holdings_data.append({
                "symbol": holding.symbol,
                "name": name,
                "quantity": holding.quantity,
                "avg_price": holding.average_price,
                "current_price": current_price,
                "portfolio": portfolio.name,
            })

        csv_content = export_portfolio_csv(holdings_data)
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=portfolio_{portfolio_id}.csv"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export portfolio CSV error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export portfolio CSV")


@router.get("/transactions/csv")
async def export_transactions_csv_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        transactions = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.created_at.desc()).all()

        tx_data = []
        for t in transactions:
            stock_row = db.query(StockModel).filter(StockModel.id == t.stock_id).first()
            symbol = stock_row.symbol if stock_row else "UNKNOWN"

            tx_data.append({
                "date": t.created_at.isoformat() if t.created_at else "",
                "symbol": symbol,
                "type": t.transaction_type,
                "quantity": t.quantity,
                "price": t.price,
                "portfolio": "Main",
            })

        csv_content = export_transactions_csv(tx_data)
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=transactions.csv"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export transactions CSV error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export transactions CSV")


@router.get("/watchlist/csv")
async def export_watchlist_csv_endpoint(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        watchlist_items = WatchListRepository(db).get_by_user_id(user.id)

        wl_data = []
        for item in watchlist_items:
            stock = StockRepository(db).get_by_id(item.stock_id)
            if not stock:
                continue
            price_data = mock_provider.get_current_price(stock.symbol)
            wl_data.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "current_price": price_data.get("current_price", 0),
                "change_pct": price_data.get("change_percent", 0),
                "added_on": item.created_at.strftime("%Y-%m-%d") if item.created_at else "",
            })

        csv_content = export_watchlist_csv(wl_data)
        return StreamingResponse(
            io.StringIO(csv_content),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=watchlist.csv"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export watchlist CSV error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export watchlist CSV")


@router.get("/portfolio/{portfolio_id}/report")
async def export_portfolio_report(portfolio_id: int, format: str = Query("json", regex="^(json|csv)$"), credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")

        holdings = []
        total_value = 0.0
        total_investment = 0.0

        for holding in portfolio.holdings:
            try:
                price_data = mock_provider.get_current_price(holding.symbol)
                current_price = price_data["current_price"]
                name = price_data.get("name", holding.symbol)
            except Exception:
                current_price = holding.average_price
                name = holding.symbol

            current_value = holding.quantity * current_price
            investment_value = holding.quantity * holding.average_price
            total_value += current_value
            total_investment += investment_value

            holdings.append({
                "symbol": holding.symbol,
                "name": name,
                "quantity": holding.quantity,
                "avg_price": holding.average_price,
                "current_price": current_price,
                "portfolio": portfolio.name,
            })

        transactions = db.query(Transaction).filter(Transaction.user_id == user.id).order_by(Transaction.created_at.desc()).limit(50).all()
        tx_data = []
        for t in transactions:
            stock_row = db.query(StockModel).filter(StockModel.id == t.stock_id).first()
            tx_data.append({
                "date": t.created_at.isoformat() if t.created_at else "",
                "symbol": stock_row.symbol if stock_row else "UNKNOWN",
                "type": t.transaction_type,
                "quantity": t.quantity,
                "price": t.price,
                "portfolio": "Main",
            })

        total_pnl = total_value - total_investment
        total_pnl_pct = (total_pnl / total_investment * 100) if total_investment > 0 else 0

        portfolio_summary = {
            "total_value": round(total_value, 2),
            "total_investment": round(total_investment, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "stock_count": len(holdings),
        }

        if format == "csv":
            csv_content = export_portfolio_csv(holdings)
            return StreamingResponse(
                io.StringIO(csv_content),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=portfolio_{portfolio_id}_report.csv"},
            )

        report = export_report_json(portfolio_summary, holdings, tx_data)
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Export portfolio report error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export portfolio report")
