from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from comprehensive_indian_stocks import mock_provider

router = APIRouter(prefix="/api/v1/compare", tags=["Stock Comparator"])


def _fetch_stocks(symbols_str: str):
    symbols = [s.strip().upper() for s in symbols_str.split(",") if s.strip()]
    if not symbols:
        raise HTTPException(status_code=400, detail="At least one symbol required")
    results = []
    errors = []
    for sym in symbols:
        try:
            results.append(mock_provider.get_current_price(sym))
        except (ValueError, Exception):
            errors.append(sym)
    if not results:
        raise HTTPException(status_code=404, detail=f"No data found for symbols: {', '.join(errors)}")
    return results, errors


@router.get("/")
async def compare_stocks(symbols: str = Query(..., description="Comma-separated symbols, e.g. TCS.NS,RELIANCE.NS,INFY.NS")):
    stocks, errors = _fetch_stocks(symbols)
    comparison = []
    for s in stocks:
        high_52w = s.get("high_52w", 0)
        low_52w = s.get("low_52w", 0)
        current = s.get("current_price", 0)
        from_52w_high = round((current - high_52w) / high_52w * 100, 2) if high_52w else 0
        comparison.append({
            "symbol": s["symbol"],
            "name": s.get("name", ""),
            "sector": s.get("sector", ""),
            "market_cap_category": s.get("market_cap_category", ""),
            "current_price": s.get("current_price", 0),
            "change_1d": s.get("change_percent", 0),
            "change_1w": s.get("price_change_1w", 0),
            "change_1m": s.get("price_change_1m", 0),
            "change_3m": s.get("price_change_3m", 0),
            "change_6m": s.get("price_change_6m", 0),
            "change_1y": s.get("price_change_1y", 0),
            "pe_ratio": s.get("pe_ratio", 0),
            "pb_ratio": s.get("pb_ratio", 0),
            "roe": s.get("roe", 0),
            "debt_to_equity": s.get("debt_to_equity", 0),
            "dividend_yield": s.get("dividend_yield", 0),
            "high_52w": high_52w,
            "low_52w": low_52w,
            "from_52w_high": from_52w_high,
        })
    return {"stocks": comparison, "errors": errors, "count": len(comparison)}


@router.get("/table")
async def get_comparison_table(symbols: str = Query(...)):
    stocks, errors = _fetch_stocks(symbols)
    metrics = [
        "Symbol", "Name", "Sector", "Market Cap Category",
        "Current Price", "Change (1D)", "Change (1W)", "Change (1M)",
        "Change (3M)", "Change (6M)", "Change (1Y)",
        "P/E Ratio", "P/B Ratio", "ROE", "Debt/Equity", "Dividend Yield",
    ]
    rows = [metrics]
    for s in stocks:
        high_52w = s.get("high_52w", 0)
        current = s.get("current_price", 0)
        from_52w_high = round((current - high_52w) / high_52w * 100, 2) if high_52w else 0
        rows.append([
            s["symbol"], s.get("name", ""), s.get("sector", ""), s.get("market_cap_category", ""),
            s.get("current_price", 0), s.get("change_percent", 0),
            s.get("price_change_1w", 0), s.get("price_change_1m", 0),
            s.get("price_change_3m", 0), s.get("price_change_6m", 0),
            s.get("price_change_1y", 0),
            s.get("pe_ratio", 0), s.get("pb_ratio", 0),
            s.get("roe", 0), s.get("debt_to_equity", 0),
            s.get("dividend_yield", 0),
        ])
    return {"headers": metrics, "rows": rows, "symbols": [s["symbol"] for s in stocks], "errors": errors}


@router.get("/radar/{symbol}")
async def get_stock_radar(symbol: str):
    symbol = symbol.upper()
    try:
        stock = mock_provider.get_current_price(symbol)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Stock not found: {symbol}")

    all_stocks = mock_provider.get_all_stocks()
    sector = stock.get("sector", "")
    sector_stocks = [s for s in all_stocks if s.get("sector", "").lower() == sector.lower()]

    def safe_mean(values):
        vals = [v for v in values if v is not None and v != 0]
        return sum(vals) / len(vals) if vals else 0

    metric_keys = ["pe_ratio", "pb_ratio", "roe", "debt_to_equity", "dividend_yield", "revenue_growth"]
    metric_labels = ["P/E Ratio", "P/B Ratio", "ROE", "Debt/Equity", "Dividend Yield", "Revenue Growth"]

    values = []
    sector_avgs = []
    max_vals = []

    for key in metric_keys:
        stock_val = stock.get(key, 0) or 0
        if key == "revenue_growth":
            stock_val = stock.get("price_change_1y", 0) or 0
        values.append(stock_val)

        sector_vals = [s.get(key, 0) or 0 for s in sector_stocks]
        if key == "revenue_growth":
            sector_vals = [s.get("price_change_1y", 0) or 0 for s in sector_stocks]
        sector_avgs.append(round(safe_mean(sector_vals), 2))

        all_vals = [s.get(key, 0) or 0 for s in all_stocks]
        if key == "revenue_growth":
            all_vals = [s.get("price_change_1y", 0) or 0 for s in all_stocks]
        max_vals.append(max(all_vals) if all_vals else 1)

    return {
        "symbol": symbol,
        "name": stock.get("name", ""),
        "sector": sector,
        "metrics": metric_labels,
        "values": values,
        "sector_averages": sector_avgs,
        "max_values": max_vals,
    }
