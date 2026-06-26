from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Dict, List, Optional
from pydantic import BaseModel

from database import get_db
from sqlalchemy.orm import Session
from models import PaperAccount, PaperHolding, PaperTransaction
from repositories.user_repository import UserRepository
from core.security import verify_token
from comprehensive_indian_stocks import mock_provider

router = APIRouter(prefix="/api/v1/paper-trading", tags=["Paper Trading"])
security = HTTPBearer()

INITIAL_BALANCE = 10_00_000


def _normalize_symbol(s: str) -> str:
    return s.replace('.NS', '').replace('.BO', '').replace('.BSE', '')


class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    order_type: str = "market"
    limit_price: Optional[float] = None


def _get_user_account(db: Session, credentials: HTTPAuthorizationCredentials):
    email = verify_token(credentials.credentials)
    user = UserRepository(db).get_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    account = db.query(PaperAccount).filter(PaperAccount.user_id == user.id).first()
    if not account:
        account = PaperAccount(user_id=user.id, balance=INITIAL_BALANCE, initial_balance=INITIAL_BALANCE)
        db.add(account)
        db.commit()
        db.refresh(account)
    return account, user


def _get_holdings_with_pnl(db: Session, account: PaperAccount) -> List[Dict]:
    holdings_list = []
    holdings = db.query(PaperHolding).filter(PaperHolding.account_id == account.id).all()
    for h in holdings:
        try:
            price_data = mock_provider.get_current_price(_normalize_symbol(h.symbol))
            current_price = price_data["current_price"]
        except Exception:
            current_price = h.avg_price
        total_value = current_price * h.quantity
        cost_basis = h.avg_price * h.quantity
        pnl = total_value - cost_basis
        pnl_percent = ((current_price - h.avg_price) / h.avg_price) * 100 if h.avg_price else 0
        holdings_list.append({
            "symbol": h.symbol,
            "quantity": h.quantity,
            "avg_price": round(h.avg_price, 2),
            "current_price": round(current_price, 2),
            "total_value": round(total_value, 2),
            "cost_basis": round(cost_basis, 2),
            "pnl": round(pnl, 2),
            "pnl_percent": round(pnl_percent, 2)
        })
    return holdings_list


@router.get("/account")
async def get_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    account, user = _get_user_account(db, credentials)
    holdings = _get_holdings_with_pnl(db, account)
    total_holdings_value = sum(h["total_value"] for h in holdings)
    total_value = account.balance + total_holdings_value
    total_pnl = total_value - account.initial_balance
    total_pnl_percent = ((total_value - account.initial_balance) / account.initial_balance) * 100
    txn_count = db.query(PaperTransaction).filter(PaperTransaction.account_id == account.id).count()
    return {
        "email": user.email,
        "balance": round(account.balance, 2),
        "initial_balance": account.initial_balance,
        "total_holdings_value": round(total_holdings_value, 2),
        "total_value": round(total_value, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_percent": round(total_pnl_percent, 2),
        "holdings_count": len(holdings),
        "transaction_count": txn_count,
        "created_at": account.created_at,
        "updated_at": account.updated_at
    }


@router.post("/buy")
async def buy_stock(
    trade: TradeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    account, _ = _get_user_account(db, credentials)
    symbol = trade.symbol.upper()

    try:
        price_data = mock_provider.get_current_price(_normalize_symbol(symbol))
        current_price = price_data["current_price"]
    except Exception:
        current_price = trade.limit_price or 100.0

    price = trade.limit_price if (trade.order_type == "limit" and trade.limit_price) else current_price
    total_cost = price * trade.quantity

    if total_cost > account.balance:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: \u20b9{total_cost:,.2f}, Available: \u20b9{account.balance:,.2f}"
        )

    account.balance -= total_cost

    holding = db.query(PaperHolding).filter(
        PaperHolding.account_id == account.id,
        PaperHolding.symbol == symbol
    ).first()

    if holding:
        total_qty = holding.quantity + trade.quantity
        holding.avg_price = ((holding.avg_price * holding.quantity) + (price * trade.quantity)) / total_qty
        holding.quantity = total_qty
    else:
        holding = PaperHolding(
            account_id=account.id,
            symbol=symbol,
            quantity=trade.quantity,
            avg_price=price
        )
        db.add(holding)

    txn = PaperTransaction(
        account_id=account.id,
        symbol=symbol,
        quantity=trade.quantity,
        price=round(price, 2),
        total=round(total_cost, 2),
        order_type=trade.order_type
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return {
        "message": f"Bought {trade.quantity} shares of {symbol} at \u20b9{price:,.2f}",
        "transaction": {
            "id": txn.id,
            "type": "buy",
            "symbol": txn.symbol,
            "quantity": txn.quantity,
            "price": txn.price,
            "total": txn.total,
            "timestamp": txn.created_at
        },
        "balance": round(account.balance, 2)
    }


@router.post("/sell")
async def sell_stock(
    trade: TradeRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    account, _ = _get_user_account(db, credentials)
    symbol = trade.symbol.upper()

    holding = db.query(PaperHolding).filter(
        PaperHolding.account_id == account.id,
        PaperHolding.symbol == symbol
    ).first()

    if not holding or holding.quantity < trade.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient holdings of {symbol}")

    try:
        price_data = mock_provider.get_current_price(_normalize_symbol(symbol))
        current_price = price_data["current_price"]
    except Exception:
        current_price = trade.limit_price or 100.0

    price = trade.limit_price if (trade.order_type == "limit" and trade.limit_price) else current_price
    total_credit = price * trade.quantity

    holding.quantity -= trade.quantity
    if holding.quantity <= 0:
        db.delete(holding)

    account.balance += total_credit

    txn = PaperTransaction(
        account_id=account.id,
        symbol=symbol,
        quantity=-trade.quantity,
        price=round(price, 2),
        total=round(total_credit, 2),
        order_type=trade.order_type
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return {
        "message": f"Sold {trade.quantity} shares of {symbol} at \u20b9{price:,.2f}",
        "transaction": {
            "id": txn.id,
            "type": "sell",
            "symbol": txn.symbol,
            "quantity": txn.quantity,
            "price": txn.price,
            "total": txn.total,
            "timestamp": txn.created_at
        },
        "balance": round(account.balance, 2)
    }


@router.get("/holdings")
async def get_holdings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    account, _ = _get_user_account(db, credentials)
    holdings = _get_holdings_with_pnl(db, account)
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
async def get_transactions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    account, _ = _get_user_account(db, credentials)
    transactions = db.query(PaperTransaction).filter(
        PaperTransaction.account_id == account.id
    ).order_by(PaperTransaction.created_at.desc()).all()
    txn_list = []
    for t in transactions:
        txn_list.append({
            "id": t.id,
            "type": "buy" if t.quantity > 0 else "sell",
            "symbol": t.symbol,
            "quantity": abs(t.quantity),
            "price": t.price,
            "total": t.total,
            "timestamp": t.created_at
        })
    return {
        "transactions": txn_list,
        "count": len(txn_list)
    }


@router.post("/reset")
async def reset_account(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    account, _ = _get_user_account(db, credentials)
    db.query(PaperHolding).filter(PaperHolding.account_id == account.id).delete()
    db.query(PaperTransaction).filter(PaperTransaction.account_id == account.id).delete()
    account.balance = account.initial_balance
    db.commit()
    return {"message": "Account reset to initial state", "balance": account.initial_balance}


@router.get("/leaderboard")
async def get_leaderboard(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    accounts = db.query(PaperAccount).all()
    entries = []
    for account in accounts:
        holdings = db.query(PaperHolding).filter(PaperHolding.account_id == account.id).all()
        total_holdings_value = 0.0
        for h in holdings:
            try:
                price_data = mock_provider.get_current_price(_normalize_symbol(h.symbol))
                current_price = price_data["current_price"]
            except Exception:
                current_price = h.avg_price
            total_holdings_value += current_price * h.quantity
        total_value = account.balance + total_holdings_value
        total_return = total_value - account.initial_balance
        total_return_pct = (total_return / account.initial_balance) * 100
        username = account.user.email.split("@")[0]
        anonymized = username[:2] + "*" * max(0, len(username) - 4) + username[-2:] if len(username) > 4 else username[0] + "***"
        txn_count = db.query(PaperTransaction).filter(PaperTransaction.account_id == account.id).count()
        entries.append({
            "rank": 0,
            "username": anonymized,
            "total_return_pct": round(total_return_pct, 2),
            "total_return": round(total_return, 2),
            "total_value": round(total_value, 2),
            "trade_count": txn_count
        })
    entries.sort(key=lambda e: e["total_return_pct"], reverse=True)
    for i, entry in enumerate(entries):
        entry["rank"] = i + 1
    return {"leaderboard": entries[:limit], "count": min(len(entries), limit)}
