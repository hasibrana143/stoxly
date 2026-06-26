import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


async def _call_gemini(prompt: str) -> Optional[str]:
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not configured")
        return None

    try:
        import google.genai as genai

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "max_output_tokens": 1024,
                "temperature": 0.3,
                "top_p": 0.95,
            },
        )
        return response.text if response else None
    except ImportError:
        logger.error("google.genai library not installed")
        return None
    except Exception as e:
        logger.error("Gemini API call failed: %s", str(e), exc_info=True)
        return None


def _rule_based_analysis(
    symbol: str,
    name: str,
    price_data: Dict,
    fundamentals: Optional[Dict] = None,
) -> Dict:
    current_price = price_data.get("current_price") or price_data.get("close") or price_data.get("price", 0)

    high_52w = price_data.get("high_52w")
    low_52w = price_data.get("low_52w")
    rsi = price_data.get("rsi")
    pe_ratio = fundamentals.get("pe_ratio") if fundamentals else None
    sector_pe = fundamentals.get("sector_pe") if fundamentals else None

    near_52w_high = False
    near_52w_low = False
    if high_52w and low_52w and high_52w > low_52w:
        range_pct = (current_price - low_52w) / (high_52w - low_52w) * 100
        near_52w_high = range_pct >= 90
        near_52w_low = range_pct <= 10

    if rsi is not None:
        if rsi >= 70:
            rsi_signal = "overbought"
        elif rsi <= 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"
    else:
        rsi_signal = "unknown"

    pe_signal = ""
    if pe_ratio is not None and sector_pe is not None and sector_pe > 0:
        pe_ratio_vs_sector = pe_ratio / sector_pe
        if pe_ratio_vs_sector > 1.5:
            pe_signal = "expensive"
        elif pe_ratio_vs_sector < 0.5:
            pe_signal = "undervalued"
        else:
            pe_signal = "fair"

    recent_prices = price_data.get("recent_prices") or price_data.get("prices") or []
    if not recent_prices and "close" in price_data:
        recent_prices = [price_data["close"]]
    if len(recent_prices) >= 5:
        sorted_prices = sorted(recent_prices)
        support = sorted_prices[0]
        resistance = sorted_prices[-1]
    else:
        support = round(current_price * 0.95, 2)
        resistance = round(current_price * 1.05, 2)

    summary_parts = []
    if near_52w_high:
        summary_parts.append(f"{name} ({symbol}) is trading near its 52-week high of {high_52w}")
    elif near_52w_low:
        summary_parts.append(f"{name} ({symbol}) is trading near its 52-week low of {low_52w}")
    else:
        summary_parts.append(f"{name} ({symbol}) is trading at {current_price}")

    if rsi_signal == "overbought":
        summary_parts.append("with overbought RSI suggesting a potential pullback")
        rating = "Sell"
    elif rsi_signal == "oversold":
        summary_parts.append("with oversold RSI suggesting a potential bounce")
        rating = "Buy"
    else:
        summary_parts.append("with neutral momentum")
        if near_52w_high:
            rating = "Hold"
        elif near_52w_low:
            rating = "Buy"
        else:
            rating = "Hold"

    if pe_signal == "expensive":
        summary_parts.append("and elevated PE ratio relative to sector")
    elif pe_signal == "undervalued":
        summary_parts.append("and attractive PE ratio relative to sector")

    risks = []
    opportunities = []
    if near_52w_high:
        risks.append("Resistance at 52-week high may cap upside in the near term")
    if rsi_signal == "overbought":
        risks.append("Overbought conditions increase risk of short-term correction")
    if pe_signal == "expensive":
        risks.append("Premium valuation leaves little margin for error")
    if near_52w_low:
        opportunities.append("Trading at 52-week lows presents a potential value entry point")
    if rsi_signal == "oversold":
        opportunities.append("Oversold conditions may lead to a mean reversion rally")
    if pe_signal == "undervalued":
        opportunities.append("Undervalued compared to sector peers on P/E basis")
    if not opportunities:
        opportunities.append("Stable price action within 52-week range")

    target_price = None
    if resistance and current_price > 0:
        target_price = round(resistance * 1.03, 2)

    return {
        "summary": ". ".join(summary_parts) + ".",
        "rating": rating,
        "target_price": target_price,
        "key_levels": {
            "support": round(support, 2),
            "resistance": round(resistance, 2),
        },
        "risks": risks,
        "opportunities": opportunities,
    }


async def analyze_stock(
    symbol: str,
    name: str,
    price_data: Dict,
    fundamentals: Optional[Dict] = None,
) -> Dict:
    prompt = f"""You are a financial analyst. Analyze the stock {name} ({symbol}).

Current price data (JSON): {json.dumps(price_data, default=str)}
Fundamentals (JSON): {json.dumps(fundamentals or {}, default=str)}

Return ONLY valid JSON with exactly these fields:
- "summary": str (2-3 sentence analysis)
- "rating": "Strong Buy" | "Buy" | "Hold" | "Sell" | "Strong Sell"
- "target_price": float | null
- "key_levels": {{"support": float, "resistance": float}}
- "risks": list[str] (2-3 risks)
- "opportunities": list[str] (2-3 opportunities)"""

    result = await _call_gemini(prompt)
    if result:
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1]
                cleaned = cleaned.rsplit("```", 1)[0]
            parsed = json.loads(cleaned.strip())
            parsed.setdefault("key_levels", {"support": None, "resistance": None})
            parsed.setdefault("risks", [])
            parsed.setdefault("opportunities", [])
            return parsed
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning("Failed to parse Gemini response for %s: %s", symbol, e)

    return _rule_based_analysis(symbol, name, price_data, fundamentals)


async def compare_stocks(stocks: List[Dict]) -> str:
    if not stocks:
        return "No stocks provided for comparison."

    prompt = f"""Compare the following stocks for investment purposes.

Stocks:
{json.dumps(stocks, indent=2, default=str)}

Provide a concise comparison covering:
1. Relative strengths and weaknesses
2. Valuation comparison
3. Growth prospects
4. Risk assessment
5. Which is better suited for different investment styles

Keep it under 500 words. Write in natural language paragraphs."""

    result = await _call_gemini(prompt)
    if result:
        return result

    names = [s.get("name", s.get("symbol", "Unknown")) for s in stocks]
    return (
        f"Comparison of {', '.join(names)}:\n\n"
        "Each stock has unique characteristics. Consider your investment horizon, "
        "risk tolerance, and diversification needs when choosing between them. "
        "Review detailed financial metrics and recent quarterly reports for each "
        "before making an investment decision."
    )


async def generate_market_brief(
    market_data: Dict,
    top_gainers: List,
    top_losers: List,
    sector_data: List,
) -> str:
    prompt = f"""You are a market analyst. Generate a daily market brief.

Market Data:
{json.dumps(market_data, default=str)}

Top Gainers:
{json.dumps(top_gainers[:10], default=str)}

Top Losers:
{json.dumps(top_losers[:10], default=str)}

Sector Performance:
{json.dumps(sector_data, default=str)}

Write a professional market brief with these sections:
1. **Market Overview** - Summary of the day's market performance
2. **Sector Watch** - Best and worst performing sectors
3. **Stocks in Focus** - Notable movers and why
4. **Outlook** - What to watch for in the coming session

Keep it under 400 words. Write in professional tone."""

    result = await _call_gemini(prompt)
    if result:
        return result

    gainers_str = ", ".join(
        f"{s.get('symbol', s.get('name', '?'))} ({s.get('change_percent', 0):+.2f}%)"
        for s in top_gainers[:5]
    ) if top_gainers else "None"

    losers_str = ", ".join(
        f"{s.get('symbol', s.get('name', '?'))} ({s.get('change_percent', 0):+.2f}%)"
        for s in top_losers[:5]
    ) if top_losers else "None"

    date_str = datetime.now().strftime("%B %d, %Y")

    return (
        f"# Market Brief – {date_str}\n\n"
        "## Market Overview\n"
        f"Markets showed mixed activity today. "
        f"Top gainers include {gainers_str}, while top losers include {losers_str}.\n\n"
        "## Sector Watch\n"
        "Sector performance varied with rotational activity across industries. "
        "Investors are closely monitoring global cues and macroeconomic data.\n\n"
        "## Stocks in Focus\n"
        "Key movers were driven by sector-specific news and earnings expectations.\n\n"
        "## Outlook\n"
        "Markets may remain influenced by global trends, institutional flows, "
        "and upcoming economic data releases. Stay tuned for further developments."
    )
