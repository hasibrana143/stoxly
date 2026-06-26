from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import statistics

from core.security import verify_token
from comprehensive_indian_stocks import mock_provider

router = APIRouter(prefix="/api/v1/paper-trading", tags=["Paper Trading"])
security = HTTPBearer()

_paper_accounts: Dict[str, Dict] = {}

INITIAL_BALANCE = 10_00_000


def _get_or_create_account(email: str) -> Dict:
    if email not in _paper_accounts:
        _paper_accounts[email] = {
            "email": email,
            "balance": INITIAL_BALANCE,
            "initial_balance": INITIAL_BALANCE,
            "holdings": {},
            "transactions": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    return _paper_accounts[email]


def _get_holdings_with_pnl(account: Dict) -> List[Dict]:
    holdings_list = []
    for symbol, holding in account["holdings"].items():
        try:
            price_data = mock_provider.get_current_price(symbol)
            current_price = price_data["current_price"]
        except Exception:
            current_price = holding["avg_price"]
        total_value = current_price * holding["quantity"]
        cost_basis = holding["avg_price"] * holding["quantity"]
        pnl = total_value - cost_basis
        pnl_percent = ((current_price - holding["avg_price"]) / holding["avg_price"]) * 100 if holding["avg_price"] else 0
        holdings_list.append({
            "symbol": symbol,
            "quantity": holding["quantity"],
            "avg_price": round(holding["avg_price"], 2),
            "current_price": round(current_price, 2),
            "total_value": round(total_value, 2),
            "cost_basis": round(cost_basis, 2),
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2)
        })
    return holdings_list


class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    order_type: str = "market"
    limit_price: Optional[float] = None


@router.get("/account")
async def get_account(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get paper trading account overview: balance, holdings, total_value, pnl"""
    email = verify_token(credentials.credentials)
    account = _get_or_create_account(email)
    holdings = _get_holdings_with_pnl(account)
    total_holdings_value = sum(h["total_value"] for h in holdings)
    total_value = account["balance"] + total_holdings_value
    total_pnl = total_value - account["initial_balance"]
    total_pnl_percent = ((total_value - account["initial_balance"]) / account["initial_balance"]) * 100
    return {
        "email": email,
        "balance": round(account["balance"], 2),
        "initial_balance": account["initial_balance"],
        "total_holdings_value": round(total_holdings_value, 2),
        "total_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_percent": round(total_pnl_percent, 2),
        "holdings_count": len(holdings),
        "transaction_count": len(account["transactions"]),
        "created_at": account["created_at"],
        "updated_at": account["updated_at"]
    }


@router.post("/buy")
async def buy_stock(trade: TradeRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Buy stocks in paper trading account"""
    email = verify_token(credentials.credentials)
    account = _get_or_create_account(email)

    symbol = trade.symbol.upper()

    try:
        price_data = mock_provider.get_current_price(symbol)
        current_price = price_data["current_price"]
    except Exception:
        current_price = trade.limit_price or 100.0

    price = trade.limit_price if (trade.order_type == "limit" and trade.limit_price) else current_price
    total_cost = price * trade.quantity

    if total_cost > account["balance"]:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Required: ₹{total_cost:,.2f}, Available: ₹{account['balance']:,.2f}")

    account["balance"] -= total_cost

    if symbol in account["holdings"]:
        h = account["holdings"][symbol]
        total_qty = h["quantity"] + trade.quantity
        h["avg_price"] = ((h["avg_price"] * h["quantity"]) + (price * trade.quantity)) / total_qty
        h["quantity"] = total_qty
    else:
        account["holdings"][symbol] = {"symbol": symbol, "quantity": trade.quantity, "avg_price": price}

    txn = {
        "id": str(uuid.uuid4()),
        "type": "buy",
        "symbol": symbol,
        "quantity": trade.quantity,
        "price": round(price, 2),
        "total": round(total_cost, 2),
        "timestamp": datetime.now().isoformat()
    }
    account["transactions"].append(txn)
    account["updated_at"] = datetime.now().isoformat()

    return {
        "message": f"Bought {trade.quantity} shares of {symbol} at ₹{price:,.2f}",
        "transaction": txn,
        "balance": round(account["balance"], 2)
    }


@router.post("/sell")
async def sell_stock(trade: TradeRequest, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Sell stocks from paper trading account"""
    email = verify_token(credentials.credentials)
    account = _get_or_create_account(email)

    symbol = trade.symbol.upper()

    if symbol not in account["holdings"] or account["holdings"][symbol]["quantity"] < trade.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient holdings of {symbol}")

    try:
        price_data = mock_provider.get_current_price(symbol)
        current_price = price_data["current_price"]
    except Exception:
        current_price = trade.limit_price or 100.0

    price = trade.limit_price if (trade.order_type == "limit" and trade.limit_price) else current_price
    total_credit = price * trade.quantity

    h = account["holdings"][symbol]
    h["quantity"] -= trade.quantity
    if h["quantity"] <= 0:
        del account["holdings"][symbol]

    account["balance"] += total_credit

    txn = {
        "id": str(uuid.uuid4()),
        "type": "sell",
        "symbol": symbol,
        "quantity": trade.quantity,
        "price": round(price, 2),
        "total": round(total_credit, 2),
        "timestamp": datetime.now().isoformat()
    }
    account["transactions"].append(txn)
    account["updated_at"] = datetime.now().isoformat()

    return {
        "message": f"Sold {trade.quantity} shares of {symbol} at ₹{price:,.2f}",
        "transaction": txn,
        "balance": round(account["balance"], 2)
    }


@router.get("/holdings")
async def get_holdings(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current holdings with P&L"""
    email = verify_token(credentials.credentials)
    account = _get_or_create_account(email)
    holdings = _get_holdings_with_pnl(account)
    total_holdings_value = sum(h["total_value"] for h in holdings)
    total_cost_basis = sum(h["cost_basis"] for h in holdings)
    total_pnl = sum(h["pnl"] for h in holdings)
    return {
        "holdings": holdings,
        "count": len(holdings),
        "total_value": round(total_holdings_value, 2),
        "total_cost_basis": round(total_cost_basis, 2),
        "total_pnl": round(total_pnl, 2)
    }


@router.get("/transactions")
async def get_transactions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get transaction history"""
    email = verify_token(credentials.credentials)
    account = _get_or_create_account(email)
    txn_list = sorted(account["transactions"], key=lambda t: t["timestamp"], reverse=True)
    return {
        "transactions": txn_list,
        "count": len(txn_list)
    }


@router.post("/reset")
async def reset_account(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Reset paper trading account to initial state"""
    email = verify_token(credentials.credentials)
    _paper_accounts[email] = {
        "email": email,
        "balance": INITIAL_BALANCE,
        "initial_balance": INITIAL_BALANCE,
        "holdings": {},
        "transactions": [],
        "created_at": _paper_accounts.get(email, {}).get("created_at", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
        "reset_at": datetime.now().isoformat()
    }
    return {"message": "Account reset to initial state", "balance": INITIAL_BALANCE}


@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(20, ge=1, le=100)):
    """Get top paper traders by P&L%"""
    entries = []
    for email, account in _paper_accounts.items():
        holdings = _get_holdings_with_pnl(account)
        total_holdings_value = sum(h["total_value"] for h in holdings)
        total_value = account["balance"] + total_holdings_value
        total_return = total_value - account["initial_balance"]
        total_return_pct = (total_return / account["initial_balance"]) * 100
        username = email.split("@")[0]
        anonymized = username[:2] + "*" * max(0, len(username) - 4) + username[-2:] if len(username) > 4 else username[0] + "***"
        entries.append({
            "rank": 0,
            "username": anonymized,
            "total_return_pct": round(total_return_pct, 2),
            "total_return": round(total_return, 2),
            "total_value": round(total_value, 2),
            "trade_count": len(account["transactions"])
        })

    entries.sort(key=lambda e: e["total_return_pct"], reverse=True)
    for i, entry in enumerate(entries):
        entry["rank"] = i + 1

    return {"leaderboard": entries[:limit], "count": min(len(entries), limit)}
