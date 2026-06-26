from fastapi import APIRouter, HTTPException, Depends, Body, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
import json
from datetime import datetime

from database import get_db
from core.security import verify_token
from core.config import settings
from repositories.user_repository import UserRepository
from repositories.portfolio_repository import PortfolioRepository
from services.ai_analysis import analyze_stock
from comprehensive_indian_stocks import mock_provider

router = APIRouter(prefix="/api/v1/chat", tags=["AI Chat"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

_chat_sessions: dict = {}

class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = "general"

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None
    timestamp: str

class ChatHistory(BaseModel):
    messages: List[dict]
    total: int

SYSTEM_PROMPT = """You are Stoxly AI, a knowledgeable Indian stock market assistant. You help users with:
- Stock analysis and recommendations
- Portfolio management advice
- Market insights and trends
- Investment strategies
- Technical and fundamental analysis
- Indian stock market (NSE/BSE) information
- Personal finance guidance

Be concise, factual, and include relevant data points. Never provide guaranteed returns.
Always remind users to consult a SEBI-registered advisor for personalized advice.

Current context: {context}
User portfolio summary: {portfolio_summary}
Market data: {market_data}
"""

CONTEXTUAL_SUGGESTIONS = {
    "general": [
        "How is Nifty 50 performing today?",
        "What are today's top gainers?",
        "Give me a market summary",
        "What sectors are performing well?",
        "Explain PE ratio",
    ],
    "portfolio": [
        "How is my portfolio performing?",
        "Show me my holdings summary",
        "What is my total P&L?",
        "Suggest rebalancing",
        "Analyze my diversification",
    ],
    "stock": [
        "What are the fundamentals of this stock?",
        "Show technical indicators",
        "What is the target price?",
        "Compare with peers",
        "What is the dividend history?",
    ],
    "screener": [
        "Screen stocks with high ROE",
        "Find low PE stocks",
        "Top momentum stocks",
        "High dividend yield stocks",
        "Stocks near 52-week low",
    ],
}

async def _build_portfolio_summary(user_email: str, db: Session) -> str:
    try:
        user_repo = UserRepository(db)
        portfolio_repo = PortfolioRepository(db)
        user = user_repo.get_by_email(user_email)
        if not user:
            return "No portfolio data available."
        portfolio = portfolio_repo.get_by_user_id(user.id)
        if not portfolio or not portfolio.holdings:
            return "No holdings found. Start investing to see portfolio insights!"
        total_value = sum(h.current_value or 0 for h in portfolio.holdings)
        total_investment = sum(h.invested_amount or 0 for h in portfolio.holdings)
        total_pnl = total_value - total_investment
        pnl_percent = (total_pnl / total_investment * 100) if total_investment else 0
        top_holding = max(portfolio.holdings, key=lambda h: h.current_value or 0)
        summary = (
            f"Total Holdings: {len(portfolio.holdings)}, "
            f"Total Value: ₹{total_value:,.2f}, "
            f"Total Investment: ₹{total_investment:,.2f}, "
            f"P&L: ₹{total_pnl:,.2f} ({pnl_percent:+.2f}%), "
            f"Top Holding: {top_holding.symbol} ({top_holding.quantity} shares)"
        )
        return summary
    except Exception as e:
        logger.error(f"Error building portfolio summary: {e}")
        return "Portfolio data temporarily unavailable."

async def _build_market_context(context: str) -> str:
    try:
        if context in ("stock", "screener"):
            indices = mock_provider.get_indices()
            if indices:
                nifty = indices.get("NIFTY 50", {})
                sensex = indices.get("SENSEX", {})
                return (
                    f"Nifty 50: {nifty.get('price', 'N/A')} "
                    f"({nifty.get('changePercent', 'N/A')}%), "
                    f"Sensex: {sensex.get('price', 'N/A')} "
                    f"({sensex.get('changePercent', 'N/A')}%)"
                )
        return "Market data context loaded."
    except Exception:
        return "Live market data temporarily unavailable."

def _template_response(message: str, context: str = "general") -> str:
    msg_lower = message.lower()

    if any(greet in msg_lower for greet in ["hello", "hi ", "hey", "namaste", "good morning", "good evening"]):
        return "Hello! I'm Stoxly AI. I can help you with Indian stock market analysis, portfolio insights, and investment strategies. What would you like to know?"

    if any(word in msg_lower for word in ["nifty", "sensex", "market", "index"]):
        return "Nifty 50 and Sensex are India's benchmark indices. For the latest levels, I recommend checking live data feeds. Key levels to watch: Nifty 50 support at 50 DMA and resistance at recent highs. Would you like sector-wise performance or stock-specific analysis?"

    if "reliance" in msg_lower:
        return "Reliance Industries (RELIANCE.NS) is a diversified conglomerate with interests in energy, telecom (Jio), and retail. Key metrics to analyze: PE ratio (industry avg ~25-30), Debt-to-Equity, Revenue growth (CAGR over 3 years), and segment-wise contribution. Jio and Retail are key growth drivers."

    if any(word in msg_lower for word in ["tcs", "infosys", "wipro", "tech", "it sector"]):
        return "The IT sector has shown resilience with strong deal pipelines. Key stocks: TCS, Infosys, HCL Tech, Wipro. Monitor USD/INR trends, deal wins, attrition rates, and client spending outlook. Would you like a detailed analysis of any specific IT stock?"

    if any(word in msg_lower for word in ["bank", "hdfc", "icici", "sbi", "financial"]):
        return "Banking stocks are driven by NIM trends, asset quality (GNPA), credit growth, and CASA ratios. HDFC Bank, ICICI Bank, and SBI are sector leaders. Key QoQ metrics to track: Net Interest Income, Provisions, and Loan Growth."

    if any(word in msg_lower for word in ["pnl", "profit", "loss", "return", "performance"]):
        return "To analyze your portfolio performance, check: 1) Absolute returns vs benchmark (Nifty 50). 2) Sector concentration risk. 3) Top 5 holdings weightage. 4) Stock-wise P&L with holding period. Would you like specific portfolio analysis? Try the Portfolio section for detailed metrics."

    if any(word in msg_lower for word in ["buy", "sell", "recommend", "suggest", "should i"]):
        return "I cannot provide personalized buy/sell recommendations. However, you should evaluate: 1) Fundamental health (PE, PB, ROE, Debt/Equity). 2) Technical trends (moving averages, RSI). 3) Industry outlook. 4) Your risk profile and investment horizon. Consider consulting a SEBI-registered advisor."

    if any(word in msg_lower for word in ["dividend", "bonus", "split", "corporate"]):
        return "Corporate actions like dividends, bonuses, and splits can impact stock prices. Key dates: Announcement Date, Ex-Date, Record Date, and Payment Date. Check company's historical dividend yield and payout ratio for income investing."

    if any(word in msg_lower for word in ["ipo", "fpo", "offer"]):
        return "IPO analysis checklist: 1) Business model and moat. 2) Financials (revenue growth, profitability). 3) Valuation relative to peers. 4) GMP (Grey Market Premium). 5) Lot size and subscription data. Always read the RHP before investing."

    if any(word in msg_lower for word in ["sector", "industry"]):
        return "Key sectors in Indian market: IT, Banking & Financials, Pharma, Auto, FMCG, Metals & Mining, Energy, Real Estate, PSUs. Each sector has different cyclicality and risk profiles. Would you like sector-wise performance analysis or specific sector deep dive?"

    if any(word in msg_lower for word in ["tax", "capital gain", "ltcg", "stcg"]):
        return "Indian equity taxation: LTCG (>1 year) at 10% over ₹1L. STCG (<1 year) at 15%. Securities Transaction Tax (STT) applies on trades. Dividend income is taxable as per your income slab. Consider tax-loss harvesting for optimization."

    if context == "portfolio" and any(word in msg_lower for word in ["holding", "position", "portfolio"]):
        return "Your portfolio analysis should consider: 1) Diversification across sectors. 2) Individual stock weightage (max 5-10% per stock). 3) Correlation between holdings. 4) Portfolio beta vs Nifty. 5) Rebalancing needs based on target allocation. Check your Portfolio dashboard for detailed metrics."

    return "That's a great question! Consider analyzing the stock's fundamentals including PE ratio (industry context), Debt-to-Equity (< 1 is ideal), Revenue Growth (> 15% YoY), and ROE (> 15%). Technical indicators like RSI, MACD, and Moving Averages can help with entry timing. Would you like me to analyze any specific stock in detail?"

async def _get_ai_response(message: str, system_context: str) -> str:
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [message]}],
            config={"system_instruction": system_context}
        )
        return response.text
    except Exception:
        return _template_response(message)


@router.post("/v2/message")
async def chat_message_v2(
    msg: ChatMessage,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token_data = verify_token(credentials.credentials)
    user_email = token_data.get("sub") or token_data.get("email", "unknown")

    portfolio_summary = ""
    if msg.context == "portfolio":
        portfolio_summary = await _build_portfolio_summary(user_email, db)

    market_data = await _build_market_context(msg.context)

    system_context = SYSTEM_PROMPT.format(
        context=msg.context,
        portfolio_summary=portfolio_summary,
        market_data=market_data,
    )

    response_text = await _get_ai_response(msg.message, system_context)

    suggestions = CONTEXTUAL_SUGGESTIONS.get(msg.context, CONTEXTUAL_SUGGESTIONS["general"])

    if user_email not in _chat_sessions:
        _chat_sessions[user_email] = []
    _chat_sessions[user_email].append({
        "role": "user",
        "message": msg.message,
        "context": msg.context,
        "timestamp": datetime.utcnow().isoformat(),
    })
    _chat_sessions[user_email].append({
        "role": "assistant",
        "message": response_text,
        "timestamp": datetime.utcnow().isoformat(),
    })

    if len(_chat_sessions[user_email]) > 200:
        _chat_sessions[user_email] = _chat_sessions[user_email][-200:]

    return ChatResponse(
        response=response_text,
        suggestions=suggestions[:5],
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/v2/history")
async def get_chat_history_v2(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    limit: int = 50,
):
    token_data = verify_token(credentials.credentials)
    user_email = token_data.get("sub") or token_data.get("email", "unknown")

    messages = _chat_sessions.get(user_email, [])
    limited = messages[-limit:] if len(messages) > limit else messages

    return ChatHistory(messages=limited, total=len(messages))


@router.delete("/v2/history")
async def clear_chat_history_v2(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token_data = verify_token(credentials.credentials)
    user_email = token_data.get("sub") or token_data.get("email", "unknown")

    _chat_sessions.pop(user_email, None)
    return {"status": "success", "message": "Chat history cleared"}


@router.get("/v2/suggestions")
async def get_suggestions(context: str = "general"):
    suggestions = CONTEXTUAL_SUGGESTIONS.get(context, CONTEXTUAL_SUGGESTIONS["general"])
    return {"context": context, "suggestions": suggestions[:8]}
