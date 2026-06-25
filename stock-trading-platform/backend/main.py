from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Any
import asyncio
import json
import random
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from database import get_db, engine
from decouple import config
import google.generativeai as genai
from models import (
    User, Portfolio, Stock, Transaction, InvestmentProfile as DBInvestmentProfile, 
    IndianStock, UserRecommendation, ChatHistory, UserScreenerFilter, create_tables, Holding, WatchList
)
from schemas import (
    UserCreate, UserLogin,
    PersonalizedChatMessage, PersonalizedChatResponse, UserRecommendationBase,
)
from auth import create_access_token, verify_token, get_password_hash, verify_password
from comprehensive_indian_stocks import (
    INDIAN_STOCKS_DATABASE, mock_provider, format_inr_price
)
from chatbot_data import QA_PAIRS
import profile_endpoints
from screener_service import screener_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    logger.info("Database tables created successfully")
    broadcast_task = asyncio.create_task(broadcast_stock_updates())

    db = next(get_db())
    try:
        demo_email = "demo@stoxly.ai"
        user = db.query(User).filter(User.email == demo_email).first()
        if not user:
            logger.info("Creating demo user")
            hashed_password = get_password_hash("demo123")
            demo_user = User(
                username="Demo User",
                email=demo_email,
                hashed_password=hashed_password
            )
            db.add(demo_user)
            db.commit()
    except Exception as e:
        logger.error(f"Error creating demo user: {e}")
    finally:
        db.close()

    yield
    # Shutdown
    broadcast_task.cancel()
    logger.info("Application shutting down")

# Initialize FastAPI app
app = FastAPI(
    title="Stock Trading Platform API",
    description="Comprehensive stock trading platform with AI chat and portfolio optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(profile_endpoints.router)

# Security
security = HTTPBearer()

# OpenAI client (add your API key)
# openai.api_key = "your-openai-api-key-here"

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Background task for broadcasting stock updates
async def broadcast_stock_updates():
    while True:
        try:
            # Get all stocks and simulate price changes
            stocks = mock_provider.get_all_stocks()
            updates = []
            
            for stock in stocks:
                updates.append({
                    "symbol": stock["symbol"],
                    "price": stock["current_price"],
                    "change": stock["change"],
                    "change_percent": stock["change_percent"]
                })
            
            await manager.broadcast(json.dumps({"type": "PRICE_UPDATE", "data": updates}))
            await asyncio.sleep(5)  # Update every 5 seconds
        except Exception as e:
            logger.error(f"Error broadcasting stock updates: {e}")
            await asyncio.sleep(5)

@app.websocket("/ws/stocks")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Tables are now created using lifespan event handler above

# Auth endpoints
@app.post("/api/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if user exists by email
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        # Check if username is taken
        db_username = db.query(User).filter(User.username == user.username).first()
        if db_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": db_user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@app.post("/api/auth/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token(data={"sub": db_user.email})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

# Stock data endpoints
@app.get("/api/stocks/search/{query}")
async def search_stocks(query: str):
    """Search for Indian stocks by symbol or company name"""
    try:
        search_results = mock_provider.search_stocks(query, limit=20)
        
        # Format results for frontend
        formatted_results = [
            {
                "symbol": stock["symbol"],
                "name": stock["name"],
                "exchange": stock["exchange"],
                "sector": stock["sector"],
                "market_cap_category": stock["market_cap_category"]
            }
            for stock in search_results
        ]
        
        return {"stocks": formatted_results}
    except Exception as e:
        logger.error(f"Stock search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Stock search failed")

@app.get("/api/stocks/price/{symbol}")
async def get_stock_price(symbol: str):
    """Get current Indian stock price"""
    try:
        price_data = mock_provider.get_current_price(symbol)
        
        return {
            "symbol": price_data["symbol"],
            "current_price": price_data["current_price"],
            "previous_close": price_data["previous_close"],
            "change": price_data["change"],
            "change_percent": price_data["change_percent"],
            "volume": price_data["volume"],
            "market_cap": price_data["market_cap"],
            "company_name": price_data["name"]
        }
    except ValueError as e:
        logger.error(f"Stock not found: {symbol}")
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Price fetch error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price")

@app.get("/api/stocks/history/{symbol}")
async def get_stock_history(
    symbol: str, 
    period: str = "1y",
    interval: str = "1d"
):
    """Get historical Indian stock data"""
    try:
        history_data = mock_provider.get_historical_data(symbol, period)
        
        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": history_data
        }
    except ValueError as e:
        logger.error(f"Stock not found: {symbol}")
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"History fetch error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock history")

# Portfolio endpoints
@app.post("/api/portfolio/create")
async def create_portfolio(
    portfolio: PortfolioCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        db_portfolio = Portfolio(
            name=portfolio.name,
            description=portfolio.description,
            user_id=user.id
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        
        return {
            "id": db_portfolio.id,
            "name": db_portfolio.name,
            "description": db_portfolio.description,
            "created_at": db_portfolio.created_at
        }
    except Exception as e:
        logger.error(f"Portfolio creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create portfolio")

@app.get("/api/portfolio/list")
async def list_portfolios(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """List user portfolios"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        
        return {
            "portfolios": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "created_at": p.created_at
                }
                for p in portfolios
            ]
        }
    except Exception as e:
        logger.error(f"Portfolio list error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolios")

@app.get("/api/portfolio/holdings", response_model=Dict[str, List[PortfolioHolding]])
async def get_all_holdings(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get all holdings across all portfolios"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        portfolios = db.query(Portfolio).filter(Portfolio.user_id == user.id).all()
        
        all_holdings = []
        
        for portfolio in portfolios:
            for holding in portfolio.holdings:
                # Get current price
                try:
                    price_data = mock_provider.get_current_price(holding.symbol)
                    current_price = price_data["current_price"]
                    name = price_data.get("name", holding.symbol)
                except:
                    current_price = holding.average_price
                    name = holding.symbol
                
                current_value = holding.quantity * current_price
                investment_value = holding.quantity * holding.average_price
                
                all_holdings.append({
                    "symbol": holding.symbol,
                    "name": name,
                    "quantity": holding.quantity,
                    "average_price": holding.average_price,
                    "current_price": current_price,
                    "current_value": current_value,
                    "investment_value": investment_value,
                    "pnl": current_value - investment_value,
                    "pnl_percent": ((current_value - investment_value) / investment_value * 100) if investment_value > 0 else 0,
                    "portfolio_name": portfolio.name,
                    "portfolio_id": portfolio.id
                })
        
        return {"holdings": all_holdings}
    except Exception as e:
        logger.error(f"Get all holdings error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch holdings")

@app.get("/api/portfolio/{portfolio_id}", response_model=PortfolioDetail)
async def get_portfolio_detail(
    portfolio_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get portfolio details with holdings and current value"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        # Calculate current values
        holdings_data = []
        total_value = 0
        total_investment = 0
        
        for holding in portfolio.holdings:
            # Get current price from mock provider
            try:
                price_data = mock_provider.get_current_price(holding.symbol)
                current_price = price_data["current_price"]
            except:
                current_price = holding.average_price # Fallback
                
            current_value = holding.quantity * current_price
            investment_value = holding.quantity * holding.average_price
            
            total_value += current_value
            total_investment += investment_value
            
            holdings_data.append({
                "id": holding.id,
                "portfolio_id": holding.portfolio_id,
                "symbol": holding.symbol,
                "quantity": holding.quantity,
                "average_price": holding.average_price,
                "created_at": holding.created_at,
                "current_price": current_price,
                "current_value": current_value,
                "pnl": current_value - investment_value,
                "pnl_percent": ((current_value - investment_value) / investment_value * 100) if investment_value > 0 else 0
            })
            
        return {
            "id": portfolio.id,
            "name": portfolio.name,
            "description": portfolio.description,
            "user_id": portfolio.user_id,
            "created_at": portfolio.created_at,
            "holdings": holdings_data,
            "total_value": total_value,
            "total_investment": total_investment,
            "total_pnl": total_value - total_investment,
            "total_pnl_percent": ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio detail error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio details")

@app.post("/api/portfolio/{portfolio_id}/add")
async def add_portfolio_item(
    portfolio_id: int,
    item: HoldingCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Add stock to portfolio"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        # Check if already exists
        existing_holding = db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id,
            Holding.symbol == item.symbol
        ).first()
        
        if existing_holding:
            # Update quantity and average price
            total_cost = (existing_holding.quantity * existing_holding.average_price) + (item.quantity * item.average_price)
            total_quantity = existing_holding.quantity + item.quantity
            existing_holding.quantity = total_quantity
            existing_holding.average_price = total_cost / total_quantity
        else:
            new_holding = Holding(
                portfolio_id=portfolio.id,
                symbol=item.symbol,
                quantity=item.quantity,
                average_price=item.average_price
            )
            db.add(new_holding)
            
        db.commit()
        return {"success": True, "message": "Stock added to portfolio"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add portfolio item error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add item to portfolio")

@app.delete("/api/portfolio/{portfolio_id}/items/{item_id}")
async def delete_portfolio_item(
    portfolio_id: int,
    item_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Remove stock from portfolio"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        holding = db.query(Holding).filter(
            Holding.id == item_id,
            Holding.portfolio_id == portfolio.id
        ).first()
        
        if not holding:
            raise HTTPException(status_code=404, detail="Item not found")
            
        db.delete(holding)
        db.commit()
        return {"success": True, "message": "Item removed from portfolio"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete portfolio item error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove item")

@app.put("/api/portfolio/{portfolio_id}/items/{item_id}")
async def update_portfolio_item(
    portfolio_id: int,
    item_id: int,
    item_update: HoldingUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update portfolio item"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        portfolio = db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user.id
        ).first()
        
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
            
        holding = db.query(Holding).filter(
            Holding.id == item_id,
            Holding.portfolio_id == portfolio.id
        ).first()
        
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



# Watchlist endpoints


# Market Movers endpoint
@app.get("/api/stocks/market-movers", response_model=Dict[str, List[MarketMover]])
async def get_market_movers(
    type: str = "gainers",
    limit: int = 10
):
    """Get top market movers (gainers/losers)"""
    try:
        all_stocks = mock_provider.get_all_stocks()
        
        # Sort by change percent
        if type == "gainers":
            sorted_stocks = sorted(all_stocks, key=lambda x: x["change_percent"], reverse=True)
        else: # losers
            sorted_stocks = sorted(all_stocks, key=lambda x: x["change_percent"])
            
        top_stocks = sorted_stocks[:limit]
        
        results = []
        for i, stock in enumerate(top_stocks):
            results.append({
                "rank": i + 1,
                "symbol": stock["symbol"],
                "name": stock["name"],
                "current_price": stock["current_price"],
                "change_percent": stock["change_percent"],
                "volume": stock.get("volume", 0)
            })
            
        return {"stocks": results}
    except Exception as e:
        logger.error(f"Market movers error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch market movers")

@app.get("/api/stocks/{symbol}")
async def get_stock_details_alias(symbol: str):
    """Get detailed stock information (Alias for frontend compatibility)"""
    try:
        # Try to get from mock provider first
        try:
            price_data = mock_provider.get_current_price(symbol)
            return {
                "symbol": price_data["symbol"],
                "current_price": price_data["current_price"],
                "previous_close": price_data["previous_close"],
                "change": price_data["change"],
                "change_percent": price_data["change_percent"],
                "volume": price_data["volume"],
                "market_cap": price_data.get("market_cap", 0),
                "company_name": price_data["name"],
                "pe_ratio": price_data.get("pe_ratio", 0),
                "roe": price_data.get("roe", 0),
                "roce": price_data.get("roce", 0),
                "book_value": price_data.get("book_value", 0),
                "dividend_yield": price_data.get("dividend_yield", 0),
                "price_change_1w": price_data.get("price_change_1w", 0),
                "price_change_1m": price_data.get("price_change_1m", 0),
                "price_change_3m": price_data.get("price_change_3m", 0),
                "price_change_6m": price_data.get("price_change_6m", 0),
                "price_change_1y": price_data.get("price_change_1y", 0),
                "high_52w": price_data.get("high_52w", 0),
                "low_52w": price_data.get("low_52w", 0)
            }
        except ValueError:
            # Try screener service if not found in mock provider
            stock_details = screener_service.get_stock_details(symbol)
            if stock_details:
                return stock_details
            raise HTTPException(status_code=404, detail="Stock not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stock details error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details")


# Screener endpoints (screener.in clone)
from schemas import ScreenerFilters, ScreenerResults

@app.post("/api/screener/screen")
async def screen_stocks(filters: ScreenerFilters):
    """Screen stocks with filters (screener.in functionality)"""
    try:
        results = screener_service.screen_stocks(filters)
        return results
    except Exception as e:
        logger.error(f"Stock details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details")

@app.get("/api/screener/sectors")
async def get_sector_analysis():
    """Get sector-wise analysis"""
    try:
        sector_data = screener_service.get_sector_analysis()
        return {"sectors": sector_data}
    except Exception as e:
        logger.error(f"Sector analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch sector analysis")

@app.get("/api/screener/peers/{symbol}")
async def get_peer_comparison(symbol: str):
    """Get peer comparison for a stock"""
    try:
        peer_data = screener_service.get_peer_comparison(symbol)
        if not peer_data:
            raise HTTPException(status_code=404, detail="Stock not found")
        return peer_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Peer comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch peer comparison")

@app.get("/api/screener/top/{criteria}")
async def get_top_stocks(criteria: str, limit: int = 20):
    """Get top stocks by various criteria"""
    try:
        valid_criteria = ["market_cap", "gainers_1d", "losers_1d", "volume", "screener_score", "dividend_yield"]
        if criteria not in valid_criteria:
            raise HTTPException(status_code=400, detail=f"Invalid criteria. Must be one of: {valid_criteria}")
        
        top_stocks = screener_service.get_top_stocks(criteria, min(limit, 50))
        return {"criteria": criteria, "stocks": top_stocks}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Top stocks error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch top stocks")

@app.get("/api/screener/quarters/{symbol}")
async def get_quarters(symbol: str):
    try:
        data = screener_service.get_quarterly_results(symbol)
        return {"symbol": symbol, "quarters": data}
    except Exception as e:
        logger.error(f"Quarterly results error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch quarterly results")

@app.get("/api/screener/financials/pl/{symbol}")
async def get_profit_loss(symbol: str):
    try:
        data = screener_service.get_profit_loss(symbol)
        return {"symbol": symbol, "profit_loss": data}
    except Exception as e:
        logger.error(f"Profit & Loss error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch profit & loss")

@app.get("/api/screener/financials/balance/{symbol}")
async def get_balance_sheet(symbol: str):
    try:
        data = screener_service.get_balance_sheet(symbol)
        return {"symbol": symbol, "balance_sheet": data}
    except Exception as e:
        logger.error(f"Balance sheet error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch balance sheet")

@app.get("/api/screener/financials/cashflow/{symbol}")
async def get_cash_flow(symbol: str):
    try:
        data = screener_service.get_cash_flow(symbol)
        return {"symbol": symbol, "cash_flow": data}
    except Exception as e:
        logger.error(f"Cash flow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cash flow")

@app.get("/api/screener/filters/presets")
async def get_filter_presets():
    """Get predefined filter presets"""
    presets = {
        "value_stocks": {
            "name": "Value Stocks",
            "description": "Undervalued stocks with low P/E and P/B ratios",
            "filters": {
                "pe_ratio_max": 15,
                "pb_ratio_max": 2,
                "roe_min": 15,
                "debt_to_equity_max": 1,
                "sort_by": "pe_ratio",
                "sort_order": "asc"
            }
        },
        "growth_stocks": {
            "name": "Growth Stocks",
            "description": "High growth companies with strong revenue and profit growth",
            "filters": {
                "revenue_growth_1y_min": 15,
                "profit_growth_1y_min": 20,
                "roe_min": 15,
                "sort_by": "revenue_growth_1y",
                "sort_order": "desc"
            }
        },
        "dividend_stocks": {
            "name": "Dividend Stocks",
            "description": "High dividend yielding stocks",
            "filters": {
                "dividend_yield_min": 3,
                "debt_to_equity_max": 1.5,
                "current_ratio_min": 1,
                "sort_by": "dividend_yield",
                "sort_order": "desc"
            }
        },
        "quality_stocks": {
            "name": "Quality Stocks",
            "description": "High quality companies with strong financials",
            "filters": {
                "roe_min": 20,
                "debt_to_equity_max": 0.5,
                "current_ratio_min": 1.5,
                "net_margin_min": 10,
                "sort_by": "screener_score",
                "sort_order": "desc"
            }
        },
        "nifty50": {
            "name": "Nifty 50 Stocks",
            "description": "All Nifty 50 index stocks",
            "filters": {
                "only_nifty50": True,
                "sort_by": "market_cap",
                "sort_order": "desc"
            }
        },
        "small_cap_gems": {
            "name": "Small Cap Gems",
            "description": "High potential small cap stocks",
            "filters": {
                "market_cap_category": ["small"],
                "roe_min": 15,
                "revenue_growth_1y_min": 10,
                "debt_to_equity_max": 1,
                "sort_by": "screener_score",
                "sort_order": "desc"
            }
        }
    }
    return {"presets": presets}

@app.get("/api/screener/filters/list")
async def list_user_filters(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        filters = db.query(UserScreenerFilter).filter(UserScreenerFilter.user_id == user.id).order_by(UserScreenerFilter.id.desc()).all()
        return {"filters": [
            {"id": f.id, "filter_name": f.filter_name, "filter_criteria": f.filter_criteria, "is_default": f.is_default}
        for f in filters]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List filters error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list filters")

@app.post("/api/screener/filters/save")
async def save_user_filter(payload: Dict[str, Any], credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        name = payload.get("filter_name")
        criteria = payload.get("filter_criteria")
        if not name or criteria is None:
            raise HTTPException(status_code=400, detail="Missing filter_name or filter_criteria")
        import json
        criteria_json = json.dumps(criteria)
        user_filter = UserScreenerFilter(user_id=user.id, filter_name=name, filter_criteria=criteria_json)
        db.add(user_filter)
        db.commit()
        # return updated list
        filters = db.query(UserScreenerFilter).filter(UserScreenerFilter.user_id == user.id).order_by(UserScreenerFilter.id.desc()).all()
        return {"filters": [
            {"id": f.id, "filter_name": f.filter_name, "filter_criteria": f.filter_criteria, "is_default": f.is_default}
        for f in filters]}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save filter error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save filter")

@app.delete("/api/screener/filters/{filter_id}")
async def delete_user_filter(filter_id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        filt = db.query(UserScreenerFilter).filter(UserScreenerFilter.id == filter_id, UserScreenerFilter.user_id == user.id).first()
        if not filt:
            raise HTTPException(status_code=404, detail="Filter not found")
        db.delete(filt)
        db.commit()
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete filter error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete filter")

# Indian Stocks endpoints (for Home page and stock listing)


# Watchlist Endpoints
@app.get("/api/watchlist")
async def get_watchlist(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        watchlist_items = db.query(WatchList).filter(WatchList.user_id == user.id).all()
        
        result = []
        for item in watchlist_items:
            stock = db.query(Stock).filter(Stock.id == item.stock_id).first()
            if stock:
                # Get real-time data
                price_data = mock_provider.get_current_price(stock.symbol)
                
                result.append({
                    "id": item.id,
                    "stock_id": stock.id,
                    "symbol": stock.symbol,
                    "name": stock.name,
                    "current_price": price_data.get("current_price", 0),
                    "change": price_data.get("change", 0),
                    "change_percent": price_data.get("change_percent", 0),
                    "market_cap": price_data.get("market_cap", 0),
                    "pe_ratio": price_data.get("pe_ratio", 0)
                })
                
        return {"watchlist": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch watchlist")

@app.post("/api/watchlist")
async def add_to_watchlist(payload: Dict[str, str], credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        symbol = payload.get("symbol")
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
            
        # Check if stock exists in DB, if not create it
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            # Fetch details from provider to create stock record
            stock_data = mock_provider.get_current_price(symbol)
            stock = Stock(
                symbol=symbol,
                name=stock_data.get("name", symbol),
                exchange=stock_data.get("exchange", "NSE"),
                sector=stock_data.get("sector", "Unknown"),
                market_cap=stock_data.get("market_cap", 0)
            )
            db.add(stock)
            db.commit()
            db.refresh(stock)
            
        # Check if already in watchlist
        existing = db.query(WatchList).filter(WatchList.user_id == user.id, WatchList.stock_id == stock.id).first()
        if existing:
            return {"message": "Stock already in watchlist", "id": existing.id}
            
        new_item = WatchList(user_id=user.id, stock_id=stock.id)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        return {"message": "Added to watchlist", "id": new_item.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add to watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")

@app.delete("/api/watchlist/{id}")
async def remove_from_watchlist(id: int, credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        item = db.query(WatchList).filter(WatchList.id == id, WatchList.user_id == user.id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Watchlist item not found")
            
        db.delete(item)
        db.commit()
        
        return {"message": "Removed from watchlist"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Remove from watchlist error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to remove from watchlist")




# Investment Profile endpoints



# AI Chat endpoint
@app.post("/api/chat", response_model=PersonalizedChatResponse)
async def chat_with_ai(
    message: PersonalizedChatMessage,
    db: Session = Depends(get_db)
):
    """Chat with AI about stocks and market analysis (Public Access)"""
    try:
        # Optional: Try to identify user if token is present in headers (not enforced)
        # For now, we'll treat all as anonymous or handle user lookup if we want to keep history
        # But for "public" access, we skip strict token verification
        user = None
        user_profile_considered = False
        profile = None
        
        # If we want to support optional auth in future, we can check headers here
        # For now, proceed without user context
        
        # --- Rule-Based Chatbot Logic ---
        user_msg = message.message.lower()
        response_text = ""
        recommendations = []

        # Check Q&A Knowledge Base
        for qa in QA_PAIRS:
            for keyword in qa["keywords"]:
                if keyword in user_msg:
                    response_text = qa["answer"]
                    return {
                        "message": message.message,
                        "response": response_text,
                        "recommendations": [],
                        "timestamp": datetime.now().isoformat(),
                        "user_profile_considered": user_profile_considered
                    }
        
        # 1. Identify Stock Symbols
        found_stocks = []
        # Use static database for search to avoid API timeout
        from stock_data_list import INDIAN_STOCKS_DATABASE
        
        for stock in INDIAN_STOCKS_DATABASE:
            # Check for symbol or name match
            # Clean stock name for better matching (remove Ltd, Limited, etc.)
            clean_name = stock["name"].lower().replace(" ltd", "").replace(" limited", "").replace(" industries", "").strip()
            
            if (stock["symbol"].lower() in user_msg or 
                clean_name in user_msg or 
                user_msg in clean_name): # Handle "Reliance" in "Reliance Industries"
                
                # Fetch live price ONLY for matched stock
                try:
                    live_data = mock_provider.get_current_price(stock["symbol"])
                    found_stocks.append(live_data)
                except Exception as e:
                    logger.error(f"Error fetching live data for {stock['symbol']}: {e}")
                    # Fallback to static data with defaults
                    fallback_stock = stock.copy()
                    fallback_stock.update({
                        "current_price": 0.0,
                        "change": 0.0,
                        "change_percent": 0.0,
                        "volume": 0,
                        "market_cap": 0
                    })
                    found_stocks.append(fallback_stock)
                
                # Limit to 2 stocks to avoid overwhelming response
                if len(found_stocks) >= 2:
                    break
        
        # 2. Generate Response using Gemini API
        gemini_success = False
        GEMINI_API_KEY = config('GEMINI_API_KEY', default=None)
        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Construct prompt with context
                context = f"User Message: {message.message}\n"
                
                if found_stocks:
                    context += "Live Stock Data:\n"
                    for stock in found_stocks:
                        context += f"- {stock['name']} ({stock['symbol']}): Price ₹{stock['current_price']}, Change {stock['change_percent']}%, Market Cap ₹{stock.get('market_cap', 0)/10000000:.2f} Cr, P/E {stock.get('pe_ratio', 'N/A')}\n"
                
                if user_profile_considered and profile:
                    context += f"User Profile: Risk Level={profile.risk_level}, Timeline={profile.timeline}, Goals={profile.investment_goals}\n"
                
                system_instruction = "You are an expert financial advisor for the Indian stock market. Use the provided live stock data to answer the user's question. If the user asks for advice, consider their risk profile if provided. Be concise, professional, and helpful. Disclaimer: Always mention that you are an AI and this is not financial advice."
                
                prompt = f"{system_instruction}\n\n{context}\n\nAnswer:"
                
                response = model.generate_content(prompt)
                response_text = response.text
                gemini_success = True
                
            except Exception as e:
                logger.error(f"Gemini API Error: {e}")
                # Fallback to rule-based logic below
                pass


        if not gemini_success:
            # Fallback to Rule-Based Logic if no key
            if found_stocks:
                stock = found_stocks[0]
                price_info = f"{stock['symbol']} is trading at ₹{stock['current_price']:.2f} ({stock['change_percent']}%)."
                
                if "price" in user_msg or "value" in user_msg or "quote" in user_msg:
                    response_text = f"The current price of {stock['name']} ({stock['symbol']}) is ₹{stock['current_price']:.2f}. It is {'up' if stock['change'] > 0 else 'down'} by {stock['change_percent']}% today. Market Cap: ₹{stock.get('market_cap', 0)/10000000:.2f} Cr."
                
                elif "buy" in user_msg or "invest" in user_msg:
                    if stock['change_percent'] < -1.5:
                        response_text = f"{price_info} It's currently down, which might be a buying opportunity if you believe in the long-term fundamentals. However, always do your own research."
                        recommendations.append(UserRecommendationBase(stock_symbol=stock['symbol'], recommendation_type="buy", reason="Dip buying opportunity", confidence_score=0.75))
                    elif stock['change_percent'] > 2.0:
                        response_text = f"{price_info} It's rallying strongly today. You might want to wait for a pullback or dollar-cost average."
                        recommendations.append(UserRecommendationBase(stock_symbol=stock['symbol'], recommendation_type="hold", reason="Price rallying, wait for dip", confidence_score=0.6))
                    else:
                        response_text = f"{price_info} It's showing stable movement. Consider its P/E ratio and recent earnings before investing."
                        recommendations.append(UserRecommendationBase(stock_symbol=stock['symbol'], recommendation_type="buy", reason="Stable performance", confidence_score=0.8))
                
                elif "sell" in user_msg:
                    if stock['change_percent'] > 5.0:
                        response_text = f"{price_info} It's up significantly! If you've met your profit targets, it might be a good time to book some profits."
                    else:
                        response_text = f"{price_info} Consider holding unless you need liquidity or your investment thesis has changed."
                
                else:
                    response_text = f"Here is the latest on {stock['name']}: Current Price ₹{stock['current_price']:.2f}, Change {stock['change_percent']}%. Volume: {stock['volume']}. Sector: {stock['sector']}."
            
            # 3. General Investment Questions
            elif "market" in user_msg:
                response_text = "The Indian market is showing mixed signals. Nifty 50 stocks are reacting to global cues. It's a good time to focus on quality large-cap stocks."
            elif "portfolio" in user_msg:
                response_text = "A balanced portfolio typically consists of 50-60% equity, 30% debt, and 10% gold/others. Would you like me to analyze your risk profile?"
            elif "risk" in user_msg:
                response_text = "Risk management is key. Never invest money you can't afford to lose, and always use stop-losses for short-term trades."
            elif "hello" in user_msg or "hi" in user_msg:
                response_text = "Hello! I'm your AI Stock Advisor. Ask me about any Indian stock (e.g., 'How is Reliance doing?') or general investment advice."
            else:
                # Fallback
                response_text = "I can help you with stock prices, investment advice, and market trends. Try asking 'What is the price of TCS?' or 'Should I buy HDFC Bank?'. (Configure GEMINI_API_KEY for advanced AI responses)"

            # Personalization injection
            if user_profile_considered and profile:
                if "high" in profile.risk_level.lower() and "buy" in user_msg:
                    response_text += " Given your high risk tolerance, you can also look at mid-cap opportunities."
                elif "low" in profile.risk_level.lower() and "buy" in user_msg:
                    response_text += " Since you prefer low risk, stick to these blue-chip stocks."

        result = {
            "message": message.message,
            "response": response_text,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "user_profile_considered": user_profile_considered
        }
        
        # Persist chat history (fail silently if DB issue)
        if user:
            try:
                db.add(ChatHistory(user_id=user.id, message=message.message, response=response_text))
                db.commit()
            except Exception as e:
                logger.warning(f"Failed to save chat history: {e}")
                db.rollback()
            
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        print("EXCEPTION CAUGHT IN CHAT ENDPOINT")
        import traceback
        with open("error_absolute.log", "w") as f:
            traceback.print_exc(file=f)
        # Return a friendly error instead of 500
        return {
            "message": message.message,
            "response": "I'm having trouble connecting to the market data right now. Please try again in a moment.",
            "recommendations": [],
            "timestamp": datetime.now().isoformat(),
            "user_profile_considered": False
        }

# Portfolio optimization endpoint
@app.post("/api/portfolio/optimize")
async def optimize_portfolio(
    request: OptimizationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Optimize portfolio allocation using Modern Portfolio Theory"""
    try:
        user_email = verify_token(credentials.credentials)
        
        # Use mock data for portfolio optimization
        symbols = request.symbols
        
        # Generate mock returns for demonstration
        # In a real application, you'd use actual historical data
        np.random.seed(42)  # For consistent results
        
        # Mock expected annual returns (8-15%)
        expected_returns = np.random.uniform(0.08, 0.15, len(symbols))
        
        # Mock covariance matrix (simplified)
        correlation_matrix = np.random.uniform(0.1, 0.8, (len(symbols), len(symbols)))
        np.fill_diagonal(correlation_matrix, 1.0)
        volatilities = np.random.uniform(0.15, 0.35, len(symbols))
        cov_matrix = np.outer(volatilities, volatilities) * correlation_matrix
        
        # Optimization function
        def portfolio_stats(weights):
            portfolio_return = np.sum(expected_returns * weights)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
            return portfolio_return, portfolio_risk, sharpe_ratio
        
        # Objective function (minimize negative Sharpe ratio)
        def negative_sharpe(weights):
            return -portfolio_stats(weights)[2]
        
        # Constraints
        constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
        bounds = tuple((0, 1) for _ in range(len(symbols)))
        
        # Initial guess (equal weights)
        initial_guess = np.array([1/len(symbols)] * len(symbols))
        
        # Optimize
        result = minimize(
            negative_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        if result.success:
            optimal_weights = result.x
            opt_return, opt_risk, opt_sharpe = portfolio_stats(optimal_weights)
            
            allocation = [
                {
                    "symbol": symbol,
                    "weight": round(weight, 4),
                    "percentage": round(weight * 100, 2)
                }
                for symbol, weight in zip(symbols, optimal_weights)
            ]
            
            return {
                "symbols": symbols,
                "allocation": allocation,
                "expected_return": round(opt_return, 4),
                "risk": round(opt_risk, 4),
                "sharpe_ratio": round(opt_sharpe, 4),
                "optimization_successful": True
            }
        else:
            raise HTTPException(status_code=500, detail="Optimization failed")
            
    except Exception as e:
        logger.error(f"Portfolio optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio optimization failed")

# Indian Stock specific endpoints
@app.get("/api/indian-stocks/all")
async def get_all_indian_stocks():
    """Get all Indian stocks with current prices in INR format"""
    try:
        stocks_data = mock_provider.get_all_stocks()
        
        # Format data for frontend with INR formatting
        formatted_stocks = []
        for stock in stocks_data:
            formatted_stocks.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "sector": stock["sector"],
                "market_cap_category": stock["market_cap_category"],
                "current_price": stock["current_price"],
                "formatted_price": format_inr_price(stock["current_price"]),
                "change": stock["change"],
                "change_percent": stock["change_percent"],
                "is_nifty50": stock["is_nifty50"],
                "is_nifty100": stock["is_nifty100"],
                "volume": stock["volume"],
                "market_cap": stock["market_cap"]
            })
        
        logger.info(f"Successfully fetched {len(formatted_stocks)} Indian stocks")
        return {"stocks": formatted_stocks}
    except Exception as e:
        logger.error(f"Indian stocks fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch Indian stocks")

@app.get("/api/indian-stocks/price/{symbol}", response_model=IndianStockPrice)
async def get_indian_stock_price(symbol: str):
    """Get current Indian stock price with INR formatting"""
    try:
        # Remove .NS suffix if present for our database lookup
        clean_symbol = symbol.replace('.NS', '')
        
        price_data = mock_provider.get_current_price(clean_symbol)
        
        return IndianStockPrice(
            symbol=clean_symbol,
            current_price=price_data["current_price"],
            previous_close=price_data["previous_close"],
            change=price_data["change"],
            change_percent=price_data["change_percent"],
            volume=price_data["volume"],
            market_cap=price_data["market_cap"],
            company_name=price_data["name"],
            currency="INR",
            formatted_price=format_inr_price(price_data["current_price"]),
            pe_ratio=15.5,  # Mock P/E ratio
            dividend_yield=0.02  # Mock dividend yield
        )
    except ValueError as e:
        logger.error(f"Stock not found: {symbol}")
        raise HTTPException(status_code=404, detail="Stock not found")
    except Exception as e:
        logger.error(f"Indian stock price fetch error for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock price")

@app.get("/api/indian-stocks/search/{query}")
async def search_indian_stocks(query: str, limit: int = 20):
    """Search Indian stocks by symbol or company name"""
    try:
        search_results = mock_provider.search_stocks(query, limit)
        
        return {"stocks": search_results}
    except Exception as e:
        logger.error(f"Indian stock search error: {str(e)}")
        raise HTTPException(status_code=500, detail="Stock search failed")

# Screener Endpoints
@app.post("/api/screener/screen", response_model=ScreenerResults)
async def screen_stocks(filters: ScreenerFilters):
    """Screen stocks based on filters"""
    try:
        return screener_service.screen_stocks(filters)
    except Exception as e:
        logger.error(f"Screening error: {str(e)}")
        raise HTTPException(status_code=500, detail="Screening failed")

@app.get("/api/screener/stock/{symbol}")
async def get_screener_stock_details(symbol: str):
    """Get detailed stock info for screener"""
    try:
        # Remove .NS suffix if present
        clean_symbol = symbol.replace('.NS', '')
        details = screener_service.get_stock_details(clean_symbol)
        if not details:
            raise HTTPException(status_code=404, detail="Stock not found")
        return details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Screener details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch stock details")

@app.get("/api/screener/quarters/{symbol}")
async def get_screener_quarters(symbol: str):
    """Get quarterly results"""
    try:
        clean_symbol = symbol.replace('.NS', '')
        quarters = screener_service.get_quarterly_results(clean_symbol)
        return {"quarters": quarters}
    except Exception as e:
        logger.error(f"Quarterly results error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch quarterly results")

@app.get("/api/screener/financials/pl/{symbol}")
async def get_screener_pl(symbol: str):
    """Get Profit & Loss statement"""
    try:
        clean_symbol = symbol.replace('.NS', '')
        pl = screener_service.get_profit_loss(clean_symbol)
        return {"profit_loss": pl}
    except Exception as e:
        logger.error(f"P&L error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch P&L")

@app.get("/api/screener/financials/balance/{symbol}")
async def get_screener_balance(symbol: str):
    """Get Balance Sheet"""
    try:
        clean_symbol = symbol.replace('.NS', '')
        balance = screener_service.get_balance_sheet(clean_symbol)
        return {"balance_sheet": balance}
    except Exception as e:
        logger.error(f"Balance sheet error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch balance sheet")

@app.get("/api/screener/financials/cashflow/{symbol}")
async def get_screener_cashflow(symbol: str):
    """Get Cash Flow statement"""
    try:
        clean_symbol = symbol.replace('.NS', '')
        cashflow = screener_service.get_cash_flow(clean_symbol)
        return {"cash_flow": cashflow}
    except Exception as e:
        logger.error(f"Cash flow error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch cash flow")

@app.get("/api/screener/peers/{symbol}")
async def get_screener_peers(symbol: str):
    """Get Peer Comparison"""
    try:
        clean_symbol = symbol.replace('.NS', '')
        peers = screener_service.get_peer_comparison(clean_symbol)
        return {"peers": peers}
    except Exception as e:
        logger.error(f"Peers error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch peers")

# Investment Profile endpoints
@app.post("/api/profile/investment", response_model=InvestmentProfile)
async def create_investment_profile(
    profile: InvestmentProfileCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create user investment profile for personalized recommendations"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        # Check if profile already exists
        existing_profile = db.query(DBInvestmentProfile).filter(
            DBInvestmentProfile.user_id == user.id
        ).first()
        
        if existing_profile:
            raise HTTPException(status_code=400, detail="Investment profile already exists")
        
        db_profile = DBInvestmentProfile(
            user_id=user.id,
            investment_amount=profile.investment_amount,
            risk_level=profile.risk_level,
            timeline=profile.timeline,
            investment_goals=profile.investment_goals,
            monthly_income=profile.monthly_income,
            age=profile.age
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return db_profile
    except Exception as e:
        logger.error(f"Investment profile creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create investment profile")

@app.get("/api/profile/investment", response_model=InvestmentProfile)
async def get_investment_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user investment profile"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        profile = db.query(DBInvestmentProfile).filter(
            DBInvestmentProfile.user_id == user.id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Investment profile not found")
        
        return profile
    except Exception as e:
        logger.error(f"Investment profile fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch investment profile")

@app.put("/api/profile/investment", response_model=InvestmentProfile)
async def update_investment_profile(
    profile_update: InvestmentProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update user investment profile"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        profile = db.query(DBInvestmentProfile).filter(
            DBInvestmentProfile.user_id == user.id
        ).first()
        
        if not profile:
            raise HTTPException(status_code=404, detail="Investment profile not found")
        
        # Update only provided fields
        for field, value in profile_update.dict(exclude_unset=True).items():
            setattr(profile, field, value)
        
        db.commit()
        db.refresh(profile)
        
        return profile
    except Exception as e:
        logger.error(f"Investment profile update error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update investment profile")

# Personalized AI Chat endpoint
@app.post("/api/chat/personalized", response_model=PersonalizedChatResponse)
async def personalized_chat(
    message: PersonalizedChatMessage,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Chat with AI using personalized investment profile context"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        # Get user's investment profile if requested
        user_profile = None
        if message.include_profile:
            user_profile = db.query(DBInvestmentProfile).filter(
                DBInvestmentProfile.user_id == user.id
            ).first()
        
        # Generate personalized response based on profile
        response = generate_personalized_response(message.message, user_profile)
        recommendations = generate_stock_recommendations(user_profile) if user_profile else None
        
        result = PersonalizedChatResponse(
            message=message.message,
            response=response,
            recommendations=recommendations,
            timestamp=datetime.now().isoformat(),
            user_profile_considered=user_profile is not None
        )
        # Persist chat history
        if user:
            db.add(ChatHistory(user_id=user.id, message=message.message, response=response))
            db.commit()
        return result
    except Exception as e:
        logger.error(f"Personalized chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")

@app.get("/api/recommendations")
async def get_user_recommendations(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get personalized stock recommendations for the user"""
    try:
        user_email = verify_token(credentials.credentials)
        user = db.query(User).filter(User.email == user_email).first()
        
        # Get user's investment profile
        user_profile = db.query(DBInvestmentProfile).filter(
            DBInvestmentProfile.user_id == user.id
        ).first()
        
        if not user_profile:
            return {"message": "Please create an investment profile to get personalized recommendations"}
        
        recommendations = generate_stock_recommendations(user_profile)
        
        return {
            "recommendations": recommendations,
            "profile": {
                "risk_level": user_profile.risk_level,
                "timeline": user_profile.timeline,
                "investment_amount": user_profile.investment_amount
            }
        }
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")

def generate_personalized_response(message: str, profile) -> str:
    """Generate personalized AI response based on user profile and real-time data"""
    
    # 1. Try OpenAI if API key is available
    openai_api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")
    if openai_api_key:
        try:
            openai.api_key = openai_api_key
            
            system_prompt = "You are a helpful financial advisor assistant for the Stoxly trading platform. You have access to Indian stock market data."
            user_context = ""
            
            if profile:
                user_context = f"""
                User Profile:
                - Risk Level: {profile.risk_level}
                - Investment Timeline: {profile.timeline}
                - Goals: {profile.investment_goals}
                - Investment Amount: ₹{profile.investment_amount}
                """
            
            # Add some market context (mock)
            market_context = "Current Market Sentiment: Mixed. Nifty 50 is trading near all-time highs."
            
            messages = [
                {"role": "system", "content": f"{system_prompt}\n{user_context}\n{market_context}"},
                {"role": "user", "content": message}
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            # Fallback to mock logic if OpenAI fails
    
    # 2. Smart Mock Logic
    message_lower = message.lower()

    # Check Q&A Knowledge Base
    for qa in QA_PAIRS:
        for keyword in qa["keywords"]:
            if keyword in message_lower:
                return qa["answer"]
    
    # Check for stock symbols in the message
    found_stocks = []
    words = re.findall(r'\b[A-Z0-9]+\b', message.upper())
    for word in words:
        # Check if it's a known stock symbol
        stock = next((s for s in INDIAN_STOCKS_DATABASE if s["symbol"] == word), None)
        if stock:
            found_stocks.append(stock)
            
    # Also check for company names
    if not found_stocks:
        for stock in INDIAN_STOCKS_DATABASE:
            if stock["name"].lower() in message_lower or stock["symbol"].lower() in message_lower:
                found_stocks.append(stock)
                if len(found_stocks) >= 3: # Limit to 3 matches
                    break
    
    if found_stocks:
        responses = []
        for stock in found_stocks[:2]: # Limit to 2 detailed stock responses
            try:
                price_data = mock_provider.get_current_price(stock["symbol"])
                price_str = format_inr_price(price_data["current_price"])
                change_str = f"{price_data['change_percent']}%"
                trend = "up" if price_data["change"] >= 0 else "down"
                
                responses.append(f"{stock['name']} ({stock['symbol']}) is currently trading at {price_str}, {trend} by {change_str} today.")
                
                # Add some fake analysis
                if profile:
                    if "high" in profile.risk_level.lower() and stock["market_cap_category"] == "small":
                        responses.append(f"As a high-risk investor, this small-cap stock aligns with your growth strategy.")
                    elif "low" in profile.risk_level.lower() and stock["market_cap_category"] == "large":
                        responses.append(f"This large-cap stock fits well with your conservative risk profile.")
            except:
                continue
                
        if responses:
            return " ".join(responses)

    # General responses based on keywords
    if "portfolio" in message_lower:
        return "Your portfolio performance depends on asset allocation. I recommend reviewing your holdings in the Portfolio section to ensure they align with your risk tolerance."
        
    if "market" in message_lower or "trend" in message_lower:
        return "The Indian market is currently showing resilience. Key sectors like Banking and IT are in focus. It's a good time to look for value opportunities."
        
    if "invest" in message_lower or "buy" in message_lower:
        if profile and "high" in profile.risk_level.lower():
            return "Given your high risk tolerance, you might consider looking at emerging mid-cap stocks or sector-specific ETFs. Always do your own research."
        else:
            return "For a balanced approach, consider blue-chip stocks with a history of consistent dividends. SIPs in index funds are also a great way to build wealth."

    # Default fallback with profile context
    if profile:
        risk_context = {
            "low": "As a conservative investor, I recommend focusing on large-cap Indian stocks like TCS, HDFCBANK, and HINDUNILVR.",
            "medium": "With moderate risk tolerance, you can diversify between large-cap stability and mid-cap growth opportunities.",
            "high": "As an aggressive investor, consider growth stocks like ZOMATO, NYKAA, or emerging sectors in the Indian market."
        }
        
        advice = risk_context.get(profile.risk_level.lower(), "Diversification is key to long-term success.")
        return f"Based on your {profile.risk_level} risk profile: {advice} How else can I assist you today?"

    return "I can help you with stock quotes, market trends, and investment advice based on your profile. Try asking about a specific stock like 'Reliance' or 'TCS'."

def generate_stock_recommendations(profile) -> List[UserRecommendationBase]:
    """Generate stock recommendations based on user profile"""
    if not profile:
        return []
    
    risk_recommendations = RISK_BASED_RECOMMENDATIONS.get(profile.risk_level, {})
    recommended_stocks = risk_recommendations.get("stocks", [])
    
    recommendations = []
    for symbol in recommended_stocks[:5]:  # Top 5 recommendations
        reason = get_stock_recommendation_reason(symbol, profile.risk_level, profile.timeline)
        recommendations.append(UserRecommendationBase(
            stock_symbol=symbol,
            recommendation_type="buy",
            confidence_score=0.8,
            reason=reason,
            target_price=None
        ))
    
    return recommendations

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
