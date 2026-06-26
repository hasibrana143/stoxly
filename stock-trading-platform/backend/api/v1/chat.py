from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from database import get_db
from schemas import PersonalizedChatMessage, PersonalizedChatResponse
from services.ai_service import generate_personalized_response, generate_stock_recommendations
from core.security import verify_token
from repositories.user_repository import UserRepository
from repositories.chat_repository import ChatHistoryRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["Chat"])


@router.post("/chat", response_model=PersonalizedChatResponse)
async def chat_with_ai(message: PersonalizedChatMessage, db: Session = Depends(get_db)):
    try:
        user_msg = message.message.lower()
        response_text = ""
        recommendations = []

        from chatbot_data import QA_PAIRS
        for qa in QA_PAIRS:
            for keyword in qa["keywords"]:
                if keyword in user_msg:
                    return {"message": message.message, "response": qa["answer"], "recommendations": [], "timestamp": datetime.now().isoformat(), "user_profile_considered": False}

        from stock_data_list import INDIAN_STOCKS_DATABASE
        found_stocks = []
        for stock in INDIAN_STOCKS_DATABASE:
            clean_name = stock["name"].lower().replace(" ltd", "").replace(" limited", "").replace(" industries", "").strip()
            if stock["symbol"].lower() in user_msg or clean_name in user_msg or user_msg in clean_name:
                try:
                    from comprehensive_indian_stocks import mock_provider
                    live_data = mock_provider.get_current_price(stock["symbol"])
                    found_stocks.append(live_data)
                except Exception as e:
                    logger.error(f"Error fetching live data for {stock['symbol']}: {e}")
                    fallback = stock.copy()
                    fallback.update({"current_price": 0.0, "change": 0.0, "change_percent": 0.0, "volume": 0, "market_cap": 0})
                    found_stocks.append(fallback)
                if len(found_stocks) >= 2:
                    break

        from decouple import config
        from google import genai as google_genai
        GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)
        gemini_success = False
        if GEMINI_API_KEY:
            try:
                client = google_genai.Client(api_key=GEMINI_API_KEY)
                context = f"User Message: {message.message}\n"
                if found_stocks:
                    context += "Live Stock Data:\n"
                    for s in found_stocks:
                        context += f"- {s['name']} ({s['symbol']}): Price ₹{s['current_price']}, Change {s['change_percent']}%, Market Cap ₹{s.get('market_cap', 0)/10000000:.2f} Cr, P/E {s.get('pe_ratio', 'N/A')}\n"
                system_instruction = "You are an expert financial advisor for the Indian stock market. Use the provided live stock data to answer the user's question. If the user asks for advice, consider their risk profile if provided. Be concise, professional, and helpful. Disclaimer: Always mention that you are an AI and this is not financial advice."
                response = client.models.generate_content(model="gemini-1.5-flash", contents=f"{system_instruction}\n\n{context}\n\nAnswer:")
                response_text = response.text
                gemini_success = True
            except Exception as e:
                logger.error(f"Gemini API Error: {e}")

        if not gemini_success:
            if found_stocks:
                stock = found_stocks[0]
                price_info = f"{stock['symbol']} is trading at ₹{stock['current_price']:.2f} ({stock['change_percent']}%)."
                if "price" in user_msg or "value" in user_msg or "quote" in user_msg:
                    response_text = f"The current price of {stock['name']} ({stock['symbol']}) is ₹{stock['current_price']:.2f}. It is {'up' if stock['change'] > 0 else 'down'} by {stock['change_percent']}% today. Market Cap: ₹{stock.get('market_cap', 0)/10000000:.2f} Cr."
                elif "buy" in user_msg or "invest" in user_msg:
                    if stock['change_percent'] < -1.5:
                        response_text = f"{price_info} It's currently down, which might be a buying opportunity if you believe in the long-term fundamentals. However, always do your own research."
                        from schemas import UserRecommendationBase
                        recommendations.append(UserRecommendationBase(stock_symbol=stock['symbol'], recommendation_type="buy", reason="Dip buying opportunity", confidence_score=0.75))
                    elif stock['change_percent'] > 2.0:
                        response_text = f"{price_info} It's rallying strongly today. You might want to wait for a pullback or dollar-cost average."
                    else:
                        response_text = f"{price_info} It's showing stable movement. Consider its P/E ratio and recent earnings before investing."
                        from schemas import UserRecommendationBase
                        recommendations.append(UserRecommendationBase(stock_symbol=stock['symbol'], recommendation_type="buy", reason="Stable performance", confidence_score=0.8))
                elif "sell" in user_msg:
                    response_text = f"{price_info} {'It is up significantly! If you have met your profit targets, it might be a good time to book some profits.' if stock['change_percent'] > 5.0 else 'Consider holding unless you need liquidity or your investment thesis has changed.'}"
                else:
                    response_text = f"Here is the latest on {stock['name']}: Current Price ₹{stock['current_price']:.2f}, Change {stock['change_percent']}%. Volume: {stock['volume']}. Sector: {stock['sector']}."
            elif "market" in user_msg:
                response_text = "The Indian market is showing mixed signals. Nifty 50 stocks are reacting to global cues. It is a good time to focus on quality large-cap stocks."
            elif "portfolio" in user_msg:
                response_text = "A balanced portfolio typically consists of 50-60% equity, 30% debt, and 10% gold/others. Would you like me to analyze your risk profile?"
            elif "risk" in user_msg:
                response_text = "Risk management is key. Never invest money you can not afford to lose, and always use stop-losses for short-term trades."
            elif "hello" in user_msg or "hi" in user_msg:
                response_text = "Hello! I am your AI Stock Advisor. Ask me about any Indian stock (e.g., 'How is Reliance doing?') or general investment advice."
            else:
                response_text = "I can help you with stock prices, investment advice, and market trends. Try asking 'What is the price of TCS?' or 'Should I buy HDFC Bank?'. (Configure GEMINI_API_KEY for advanced AI responses)"

        result = {"message": message.message, "response": response_text, "recommendations": recommendations, "timestamp": datetime.now().isoformat(), "user_profile_considered": False}
        return result
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return {"message": message.message, "response": "I am having trouble connecting to the market data right now. Please try again in a moment.", "recommendations": [], "timestamp": datetime.now().isoformat(), "user_profile_considered": False}


@router.post("/chat/personalized", response_model=PersonalizedChatResponse)
async def personalized_chat(message: PersonalizedChatMessage, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = UserRepository(db).get_by_email(user_email)
        user_profile = None
        if message.include_profile and user:
            from repositories.profile_repository import InvestmentProfileRepository
            user_profile = InvestmentProfileRepository(db).get_by_user_id(user.id)
        response = generate_personalized_response(message.message, user_profile)
        recommendations = generate_stock_recommendations(user_profile) if user_profile else None
        result = PersonalizedChatResponse(message=message.message, response=response, recommendations=recommendations, timestamp=datetime.now().isoformat(), user_profile_considered=user_profile is not None)
        if user:
            ChatHistoryRepository(db).create(user_id=user.id, message=message.message, response=response)
        return result
    except Exception as e:
        logger.error(f"Personalized chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")
