import csv
import io
from typing import List, Dict, Optional
from datetime import datetime


def _make_row(columns: List[str], row: Dict) -> List:
    return [row.get(col) if row.get(col) is not None else "" for col in columns]


def export_portfolio_csv(holdings: List[Dict]) -> str:
    """
    Generate portfolio CSV.
    Columns: Symbol, Name, Quantity, Avg Price, Current Price, Investment, Current Value, P&L, P&L%, Portfolio
    Returns CSV string.
    """
    columns = [
        "Symbol", "Name", "Quantity", "Avg Price", "Current Price",
        "Investment", "Current Value", "P&L", "P&L%", "Portfolio"
    ]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for h in holdings:
        investment = (h.get("avg_price", 0) or 0) * (h.get("quantity", 0) or 0)
        current_value = (h.get("current_price", 0) or 0) * (h.get("quantity", 0) or 0)
        pnl = current_value - investment
        investment_safe = investment if investment else 1
        pnl_pct = (pnl / investment_safe) * 100
        enriched = {
            "Symbol": h.get("symbol"),
            "Name": h.get("name"),
            "Quantity": h.get("quantity"),
            "Avg Price": h.get("avg_price"),
            "Current Price": h.get("current_price"),
            "Investment": round(investment, 2),
            "Current Value": round(current_value, 2),
            "P&L": round(pnl, 2),
            "P&L%": round(pnl_pct, 2),
            "Portfolio": h.get("portfolio"),
        }
        writer.writerow(_make_row(columns, enriched))
    return output.getvalue()


def export_transactions_csv(transactions: List[Dict]) -> str:
    """
    Generate transactions CSV.
    Columns: Date, Symbol, Type, Quantity, Price, Total, Portfolio
    Returns CSV string.
    """
    columns = ["Date", "Symbol", "Type", "Quantity", "Price", "Total", "Portfolio"]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for t in transactions:
        total = ((t.get("price", 0) or 0) * (t.get("quantity", 0) or 0))
        enriched = {
            "Date": t.get("date"),
            "Symbol": t.get("symbol"),
            "Type": t.get("type"),
            "Quantity": t.get("quantity"),
            "Price": t.get("price"),
            "Total": round(total, 2),
            "Portfolio": t.get("portfolio"),
        }
        writer.writerow(_make_row(columns, enriched))
    return output.getvalue()


def export_report_json(
    portfolio_summary: Dict,
    holdings: List[Dict],
    transactions: List[Dict],
) -> Dict:
    """
    Generate a comprehensive report as a JSON dict with:
    - summary: total_value, total_investment, total_pnl, total_pnl_pct, stock_count
    - holdings: enriched holdings data
    - performance: monthly returns if available
    - generated_at: ISO timestamp
    """
    summary = {
        "total_value": portfolio_summary.get("total_value", 0),
        "total_investment": portfolio_summary.get("total_investment", 0),
        "total_pnl": portfolio_summary.get("total_pnl", 0),
        "total_pnl_pct": portfolio_summary.get("total_pnl_pct", 0),
        "stock_count": portfolio_summary.get("stock_count", len(holdings)),
    }

    enriched_holdings = []
    for h in holdings:
        investment = (h.get("avg_price", 0) or 0) * (h.get("quantity", 0) or 0)
        current_value = (h.get("current_price", 0) or 0) * (h.get("quantity", 0) or 0)
        pnl = current_value - investment
        investment_safe = investment if investment else 1
        pnl_pct = (pnl / investment_safe) * 100
        enriched_holdings.append({
            "symbol": h.get("symbol"),
            "name": h.get("name"),
            "quantity": h.get("quantity"),
            "avg_price": h.get("avg_price"),
            "current_price": h.get("current_price"),
            "investment": round(investment, 2),
            "current_value": round(current_value, 2),
            "pnl": round(pnl, 2),
            "pnl_pct": round(pnl_pct, 2),
            "portfolio": h.get("portfolio"),
        })

    monthly_returns = portfolio_summary.get("monthly_returns")

    return {
        "summary": summary,
        "holdings": enriched_holdings,
        "transactions": transactions,
        "performance": {"monthly_returns": monthly_returns} if monthly_returns else {},
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def export_watchlist_csv(watchlist: List[Dict]) -> str:
    """
    Generate watchlist CSV.
    Columns: Symbol, Name, Current Price, Change%, Added On
    Returns CSV string.
    """
    columns = ["Symbol", "Name", "Current Price", "Change%", "Added On"]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(columns)
    for w in watchlist:
        enriched = {
            "Symbol": w.get("symbol"),
            "Name": w.get("name"),
            "Current Price": w.get("current_price"),
            "Change%": w.get("change_pct"),
            "Added On": w.get("added_on"),
        }
        writer.writerow(_make_row(columns, enriched))
    return output.getvalue()
