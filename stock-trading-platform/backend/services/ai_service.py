import re
import os
import logging
from typing import List, Optional

from comprehensive_indian_stocks import mock_provider, format_inr_price, INDIAN_STOCKS_DATABASE
from chatbot_data import QA_PAIRS
from schemas import UserRecommendationBase

logger = logging.getLogger(__name__)


def generate_stock_recommendations(profile) -> List[UserRecommendationBase]:
    if not profile:
        return []
    risk_recommendations = RISK_BASED_RECOMMENDATIONS.get(profile.risk_level, {})
    recommended_stocks = risk_recommendations.get("stocks", [])
    recommendations = []
    for symbol in recommended_stocks[:5]:
        reason = get_stock_recommendation_reason(symbol, profile.risk_level, profile.timeline)
        recommendations.append(UserRecommendationBase(stock_symbol=symbol, recommendation_type="buy", confidence_score=0.8, reason=reason, target_price=None))
    return recommendations


def generate_personalized_response(message: str, profile) -> str:
    message_lower = message.lower()

    for qa in QA_PAIRS:
        for keyword in qa["keywords"]:
            if keyword in message_lower:
                return qa["answer"]

    found_stocks = []
    words = re.findall(r'\b[A-Z0-9]+\b', message.upper())
    for word in words:
        stock = next((s for s in INDIAN_STOCKS_DATABASE if s["symbol"] == word), None)
        if stock:
            found_stocks.append(stock)

    if not found_stocks:
        for stock in INDIAN_STOCKS_DATABASE:
            if stock["name"].lower() in message_lower or stock["symbol"].lower() in message_lower:
                found_stocks.append(stock)
                if len(found_stocks) >= 3:
                    break

    if found_stocks:
        responses = []
        for stock in found_stocks[:2]:
            try:
                price_data = mock_provider.get_current_price(stock["symbol"])
                price_str = format_inr_price(price_data["current_price"])
                change_str = f"{price_data['change_percent']}%"
                trend = "up" if price_data["change"] >= 0 else "down"
                responses.append(f"{stock['name']} ({stock['symbol']}) is currently trading at {price_str}, {trend} by {change_str} today.")
                if profile:
                    if "high" in profile.risk_level.lower() and stock["market_cap_category"] == "small":
                        responses.append(f"As a high-risk investor, this small-cap stock aligns with your growth strategy.")
                    elif "low" in profile.risk_level.lower() and stock["market_cap_category"] == "large":
                        responses.append(f"This large-cap stock fits well with your conservative risk profile.")
            except Exception:
                continue
        if responses:
            return " ".join(responses)

    if "portfolio" in message_lower:
        return "Your portfolio performance depends on asset allocation. I recommend reviewing your holdings in the Portfolio section to ensure they align with your risk tolerance."
    if "market" in message_lower or "trend" in message_lower:
        return "The Indian market is currently showing resilience. Key sectors like Banking and IT are in focus. It is a good time to look for value opportunities."
    if "invest" in message_lower or "buy" in message_lower:
        if profile and "high" in profile.risk_level.lower():
            return "Given your high risk tolerance, you might consider looking at emerging mid-cap stocks or sector-specific ETFs. Always do your own research."
        return "For a balanced approach, consider blue-chip stocks with a history of consistent dividends. SIPs in index funds are also a great way to build wealth."

    if profile:
        risk_context = {"low": "As a conservative investor, I recommend focusing on large-cap Indian stocks like TCS, HDFCBANK, and HINDUNILVR.", "medium": "With moderate risk tolerance, you can diversify between large-cap stability and mid-cap growth opportunities.", "high": "As an aggressive investor, consider growth stocks like ZOMATO, NYKAA, or emerging sectors in the Indian market."}
        advice = risk_context.get(profile.risk_level.lower(), "Diversification is key to long-term success.")
        return f"Based on your {profile.risk_level} risk profile: {advice} How else can I assist you today?"

    return "I can help you with stock quotes, market trends, and investment advice based on your profile. Try asking about a specific stock like 'Reliance' or 'TCS'."


def get_stock_recommendation_reason(symbol: str, risk_level: str, timeline: str) -> str:
    reasons = {
        "RELIANCE": "Strong fundamentals across retail, telecom, and energy sectors with consistent growth",
        "TCS": "Market leader in IT services with strong global presence and consistent dividend history",
        "HDFCBANK": "Strong banking fundamentals with high asset quality and consistent NII growth",
        "INFY": "Strong IT services company with robust digital transformation pipeline",
        "ICICIBANK": "Well capitalized with strong retail and corporate banking franchise",
        "SBIN": "India's largest bank with strong government backing and wide network",
        "HINDUNILVR": "Market leader in FMCG with consistent revenue and profit growth",
        "ITC": "Diversified conglomerate with strong cash flows and high dividend yield",
        "DMART": "Leading retail chain with strong operational efficiency and growth",
        "TATAMOTORS": "Strong EV transition play with improving JLR performance",
        "HAL": "Monopoly in aerospace with strong order book and government backing",
        "MOTHERSON": "Global auto component leader with strong EV transition strategy",
        "ZOMATO": "Market leader in food delivery with improving unit economics",
        "PIDILITIND": "Market leader in adhesives and chemicals with strong brand moat",
        "ASIANPAINT": "Market leader in paints with strong distribution network",
        "NYKAA": "Leading beauty and cosmetics player with strong omnichannel presence",
        "MARUTI": "India's largest car manufacturer with strong EV transition plans",
        "BAJFINANCE": "Leading NBFC with strong asset quality and growth metrics",
        "KOTAKBANK": "Strong retail banking franchise with high profitability ratios",
        "LT": "Engineering and construction leader with strong order book",
    }
    return reasons.get(symbol, "Strong market position with good growth prospects")


RISK_BASED_RECOMMENDATIONS = {
    "low": {
        "stocks": ["TCS", "HDFCBANK", "HINDUNILVR", "ITC", "INFY", "RELIANCE", "MARUTI"],
        "allocation": {"large_cap": 70, "mid_cap": 20, "small_cap": 10},
        "strategy": "Focus on blue-chip stocks with consistent dividends and lower volatility"
    },
    "medium": {
        "stocks": ["ICICIBANK", "SBIN", "BAJFINANCE", "LT", "KOTAKBANK", "DMART", "PIDILITIND", "ASIANPAINT"],
        "allocation": {"large_cap": 50, "mid_cap": 30, "small_cap": 20},
        "strategy": "Balanced portfolio with growth and stability mix"
    },
    "high": {
        "stocks": ["TATAMOTORS", "HAL", "MOTHERSON", "ZOMATO", "NYKAA", "DMART", "PIDILITIND"],
        "allocation": {"large_cap": 30, "mid_cap": 40, "small_cap": 30},
        "strategy": "Focus on high growth sectors with mid-cap and small-cap exposure"
    }
}
