import numpy as np
import random
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel

from database import get_db
from core.security import verify_token
from services.portfolio_optimizer import optimize_portfolio, rebalance_suggestion, calculate_var, calculate_cvar, black_litterman
from services.technical_indicators import calculate_sma, calculate_ema, calculate_rsi, calculate_macd
from repositories.portfolio_repository import PortfolioRepository
from comprehensive_indian_stocks import mock_provider

router = APIRouter(prefix="/api/v1/portfolio", tags=["Portfolio"])
security = HTTPBearer()

class OptimizeRequest(BaseModel):
    symbols: List[str]
    risk_free_rate: float = 0.065

class RebalanceRequest(BaseModel):
    current_weights: Dict[str, float]
    target_weights: Dict[str, float]
    threshold: float = 0.05

class BlackLittermanRequest(BaseModel):
    market_caps: Dict[str, float]
    views: List[Dict]
    confidence: float = 0.5

def _generate_sample_returns(symbols: List[str], days: int = 252) -> Dict[str, List[float]]:
    n = len(symbols)
    mean = 0.001
    cov_base = 0.02
    corr = np.eye(n)
    for i in range(n):
        for j in range(i + 1, n):
            r = random.uniform(0.3, 0.7)
            corr[i][j] = r
            corr[j][i] = r
    L = np.linalg.cholesky(corr)
    uncorrelated = np.random.normal(0, cov_base, (days, n))
    correlated = uncorrelated @ L.T + mean
    return {symbols[i]: [float(correlated[d, i]) for d in range(days)] for i in range(n)}

@router.post("/optimize")
async def optimize_portfolio_endpoint(
    request: OptimizeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user_id = verify_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not request.symbols:
        raise HTTPException(status_code=400, detail="At least one symbol required")

    repo = PortfolioRepository(db)
    historical_data = {}
    for symbol in request.symbols:
        prices = repo.get_historical_prices(user_id, symbol)
        if prices and len(prices) >= 30:
            returns = [float(prices[i]) / float(prices[i + 1]) - 1 for i in range(len(prices) - 1)]
            historical_data[symbol] = returns

    if len(historical_data) < len(request.symbols):
        missing = [s for s in request.symbols if s not in historical_data]
        fallback = _generate_sample_returns(missing, days=252)
        historical_data.update(fallback)

    returns_matrix = np.array([historical_data[s][:252] for s in request.symbols]).T
    result = optimize_portfolio(returns_matrix, request.risk_free_rate)
    result["symbols"] = request.symbols
    return result

@router.post("/rebalance")
async def rebalance_portfolio(
    request: RebalanceRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user_id = verify_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    all_symbols = set(list(request.current_weights.keys()) + list(request.target_weights.keys()))
    trades = []
    for symbol in sorted(all_symbols):
        current_w = request.current_weights.get(symbol, 0.0)
        target_w = request.target_weights.get(symbol, 0.0)
        diff = target_w - current_w
        if abs(diff) >= request.threshold:
            action = "buy" if diff > 0 else "sell"
            trades.append({
                "symbol": symbol,
                "current_weight": current_w,
                "target_weight": target_w,
                "diff": round(diff, 4),
                "action": action
            })
    return {"trades": trades, "total_trades": len(trades)}

@router.get("/risk/{portfolio_id}")
async def get_portfolio_risk(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user_id = verify_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    repo = PortfolioRepository(db)
    portfolio = repo.get_portfolio(portfolio_id)
    if not portfolio or portfolio.user_id != user_id:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    symbol_weights = repo.get_holdings(portfolio_id)
    if not symbol_weights:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")

    symbols = list(symbol_weights.keys())
    weights = np.array([symbol_weights[s] for s in symbols])

    historical_data = {}
    for symbol in symbols:
        prices = repo.get_historical_prices(user_id, symbol)
        if prices and len(prices) >= 30:
            returns = [float(prices[i]) / float(prices[i + 1]) - 1 for i in range(len(prices) - 1)]
            historical_data[symbol] = returns

    if len(historical_data) < len(symbols):
        missing = [s for s in symbols if s not in historical_data]
        fallback = _generate_sample_returns(missing, days=252)
        historical_data.update(fallback)

    returns_matrix = np.array([historical_data[s][:252] for s in symbols])
    result = calculate_var(returns_matrix, weights)
    cvar_result = calculate_cvar(returns_matrix, weights)
    result.update(cvar_result)
    result["volatility"] = float(np.sqrt(np.dot(weights.T, np.dot(np.cov(returns_matrix), weights))))
    try:
        market_returns = np.mean(returns_matrix, axis=0)
        portfolio_returns = np.dot(weights, returns_matrix)
        cov_with_market = np.cov(portfolio_returns, market_returns)[0, 1]
        market_var = np.var(market_returns)
        result["beta_to_market"] = round(float(cov_with_market / market_var), 4) if market_var > 0 else 1.0
    except Exception:
        result["beta_to_market"] = 1.0
    return result

@router.post("/black-litterman")
async def black_litterman_endpoint(
    request: BlackLittermanRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        user_id = verify_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not request.market_caps:
        raise HTTPException(status_code=400, detail="market_caps is required")

    symbols = list(request.market_caps.keys())
    market_caps = np.array([request.market_caps[s] for s in symbols])
    market_weights = market_caps / market_caps.sum()

    n = len(symbols)
    sample_returns = _generate_sample_returns(symbols, days=252)
    returns_matrix = np.array([sample_returns[s] for s in symbols])
    cov_matrix = np.cov(returns_matrix)

    result = black_litterman(cov_matrix, market_weights, request.views, request.confidence)
    result["symbols"] = symbols
    return result

@router.get("/efficient-frontier/{portfolio_id}")
async def get_efficient_frontier(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        user_id = verify_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    repo = PortfolioRepository(db)
    portfolio = repo.get_portfolio(portfolio_id)
    if not portfolio or portfolio.user_id != user_id:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    symbol_weights = repo.get_holdings(portfolio_id)
    if not symbol_weights:
        raise HTTPException(status_code=400, detail="Portfolio has no holdings")

    symbols = list(symbol_weights.keys())

    historical_data = {}
    for symbol in symbols:
        prices = repo.get_historical_prices(user_id, symbol)
        if prices and len(prices) >= 30:
            returns = [float(prices[i]) / float(prices[i + 1]) - 1 for i in range(len(prices) - 1)]
            historical_data[symbol] = returns

    if len(historical_data) < len(symbols):
        missing = [s for s in symbols if s not in historical_data]
        fallback = _generate_sample_returns(missing, days=252)
        historical_data.update(fallback)

    returns_matrix = np.array([historical_data[s][:252] for s in symbols])
    mean_returns = np.mean(returns_matrix, axis=1)
    cov_matrix = np.cov(returns_matrix)

    num_portfolios = 50
    results = []
    for _ in range(num_portfolios):
        weights = np.random.random(len(symbols))
        weights = weights / weights.sum()
        port_return = np.dot(weights, mean_returns)
        port_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe = port_return / port_volatility if port_volatility > 0 else 0
        results.append({
            "return": round(float(port_return * 252), 4),
            "volatility": round(float(port_volatility * np.sqrt(252)), 4),
            "sharpe": round(float(sharpe * np.sqrt(252)), 4)
        })

    results.sort(key=lambda x: x["volatility"])

    max_sharpe = max(results, key=lambda x: x["sharpe"])
    min_vol = min(results, key=lambda x: x["volatility"])

    return {
        "frontier": results,
        "max_sharpe_portfolio": max_sharpe,
        "min_volatility_portfolio": min_vol,
        "symbols": symbols
    }
