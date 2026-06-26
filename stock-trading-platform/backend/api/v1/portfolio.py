from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import Dict, List
import logging
import numpy as np
from scipy.optimize import minimize

from database import get_db
from schemas import PortfolioCreate, HoldingCreate, HoldingUpdate, PortfolioDetail, PortfolioHolding, OptimizationRequest
from core.security import verify_token
from comprehensive_indian_stocks import mock_provider
from repositories.user_repository import UserRepository
from repositories.portfolio_repository import PortfolioRepository, HoldingRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])


def _get_user(credentials: HTTPAuthorizationCredentials, db: Session):
    user_email = verify_token(credentials.credentials)
    user = UserRepository(db).get_by_email(user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/create")
async def create_portfolio(portfolio: PortfolioCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        db_portfolio = PortfolioRepository(db).create(name=portfolio.name, description=portfolio.description, user_id=user.id)
        return {"id": db_portfolio.id, "name": db_portfolio.name, "description": db_portfolio.description, "created_at": db_portfolio.created_at}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create portfolio")


@router.get("/list")
async def list_portfolios(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolios = PortfolioRepository(db).get_by_user_id(user.id)
        return {"portfolios": [{"id": p.id, "name": p.name, "description": p.description, "created_at": p.created_at} for p in portfolios]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio list error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolios")


@router.get("/holdings", response_model=Dict[str, List[PortfolioHolding]])
async def get_all_holdings(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolios = PortfolioRepository(db).get_by_user_id(user.id)
        all_holdings = []
        for portfolio in portfolios:
            for holding in portfolio.holdings:
                try:
                    price_data = mock_provider.get_current_price(holding.symbol)
                    current_price = price_data["current_price"]
                    name = price_data.get("name", holding.symbol)
                except:
                    current_price = holding.average_price
                    name = holding.symbol
                current_value = holding.quantity * current_price
                investment_value = holding.quantity * holding.average_price
                all_holdings.append({"symbol": holding.symbol, "name": name, "quantity": holding.quantity, "average_price": holding.average_price, "current_price": current_price, "current_value": current_value, "investment_value": investment_value, "pnl": current_value - investment_value, "pnl_percent": ((current_value - investment_value) / investment_value * 100) if investment_value > 0 else 0, "portfolio_name": portfolio.name, "portfolio_id": portfolio.id})
        return {"holdings": all_holdings}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get all holdings error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch holdings")


@router.get("/{portfolio_id}", response_model=PortfolioDetail)
async def get_portfolio_detail(portfolio_id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        holdings_data = []
        total_value = 0
        total_investment = 0
        for holding in portfolio.holdings:
            try:
                price_data = mock_provider.get_current_price(holding.symbol)
                current_price = price_data["current_price"]
            except:
                current_price = holding.average_price
            current_value = holding.quantity * current_price
            investment_value = holding.quantity * holding.average_price
            total_value += current_value
            total_investment += investment_value
            holdings_data.append({"id": holding.id, "portfolio_id": holding.portfolio_id, "symbol": holding.symbol, "quantity": holding.quantity, "average_price": holding.average_price, "created_at": holding.created_at, "current_price": current_price, "current_value": current_value, "pnl": current_value - investment_value, "pnl_percent": ((current_value - investment_value) / investment_value * 100) if investment_value > 0 else 0})
        return {"id": portfolio.id, "name": portfolio.name, "description": portfolio.description, "user_id": portfolio.user_id, "created_at": portfolio.created_at, "holdings": holdings_data, "total_value": total_value, "total_investment": total_investment, "total_pnl": total_value - total_investment, "total_pnl_percent": ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio detail error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio details")


@router.post("/{portfolio_id}/add")
async def add_portfolio_item(portfolio_id: int, item: HoldingCreate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        existing_holding = HoldingRepository(db).get_by_portfolio_and_symbol(portfolio.id, item.symbol)
        if existing_holding:
            total_cost = (existing_holding.quantity * existing_holding.average_price) + (item.quantity * item.average_price)
            total_quantity = existing_holding.quantity + item.quantity
            existing_holding.quantity = total_quantity
            existing_holding.average_price = total_cost / total_quantity
            db.commit()
        else:
            HoldingRepository(db).create(portfolio_id=portfolio.id, symbol=item.symbol, quantity=item.quantity, average_price=item.average_price)
        return {"success": True, "message": "Stock added to portfolio"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add portfolio item error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add item to portfolio")


@router.delete("/{portfolio_id}/items/{item_id}")
async def delete_portfolio_item(portfolio_id: int, item_id: int, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        holding = HoldingRepository(db).get_by_id_and_portfolio(item_id, portfolio.id)
        if not holding:
            raise HTTPException(status_code=404, detail="Item not found")
        HoldingRepository(db).delete(holding)
        return {"success": True, "message": "Item removed from portfolio"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete portfolio item error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove item")


@router.put("/{portfolio_id}/items/{item_id}")
async def update_portfolio_item(portfolio_id: int, item_id: int, item_update: HoldingUpdate, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user = _get_user(credentials, db)
        portfolio = PortfolioRepository(db).get_by_id_and_user(portfolio_id, user.id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        holding = HoldingRepository(db).get_by_id_and_portfolio(item_id, portfolio.id)
        if not holding:
            raise HTTPException(status_code=404, detail="Item not found")
        if item_update.quantity is not None:
            holding.quantity = item_update.quantity
        if item_update.average_price is not None:
            holding.average_price = item_update.average_price
        db.commit()
        return {"success": True, "message": "Item updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update portfolio item error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update item")


@router.post("/optimize")
async def optimize_portfolio(request: OptimizationRequest, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    try:
        verify_token(credentials.credentials)
        symbols = request.symbols
        np.random.seed(42)
        expected_returns = np.random.uniform(0.08, 0.15, len(symbols))
        correlation_matrix = np.random.uniform(0.1, 0.8, (len(symbols), len(symbols)))
        np.fill_diagonal(correlation_matrix, 1.0)
        volatilities = np.random.uniform(0.15, 0.35, len(symbols))
        cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix

        def portfolio_stats(weights):
            portfolio_return = np.sum(expected_returns * weights)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return portfolio_return, portfolio_risk, portfolio_return / portfolio_risk if portfolio_risk > 0 else 0

        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(len(symbols)))
        initial_guess = np.array([1 / len(symbols)] * len(symbols))
        result = minimize(lambda w: -portfolio_stats(w)[2], initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

        if result.success:
            opt_return, opt_risk, opt_sharpe = portfolio_stats(result.x)
            allocation = [{"symbol": s, "weight": round(w, 4), "percentage": round(w * 100, 2)} for s, w in zip(symbols, result.x)]
            return {"symbols": symbols, "allocation": allocation, "expected_return": round(opt_return, 4), "risk": round(opt_risk, 4), "sharpe_ratio": round(opt_sharpe, 4), "optimization_successful": True}
        raise HTTPException(status_code=500, detail="Optimization failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio optimization failed")
