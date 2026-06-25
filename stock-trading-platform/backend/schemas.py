from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Stock schemas
class StockBase(BaseModel):
    symbol: str
    name: str
    exchange: Optional[str] = None

class Stock(StockBase):
    id: int
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class StockPrice(BaseModel):
    symbol: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    company_name: str

class StockHistoryPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class StockHistory(BaseModel):
    symbol: str
    period: str
    interval: str
    data: List[StockHistoryPoint]

# Portfolio schemas
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None

class PortfolioCreate(PortfolioBase):
    pass

class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Transaction schemas
class TransactionBase(BaseModel):
    stock_symbol: str
    transaction_type: str
    quantity: float
    price: float

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int
    total_amount: float
    created_at: datetime
    
    class Config:
        from_attributes = True

# Chat schemas
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    message: str
    response: str
    timestamp: str

# Portfolio optimization schemas
class OptimizationRequest(BaseModel):
    symbols: List[str]
    risk_tolerance: Optional[str] = "moderate"  # low, moderate, high
    investment_horizon: Optional[str] = "medium"  # short, medium, long

class AllocationItem(BaseModel):
    symbol: str
    weight: float
    percentage: float

class OptimizationResult(BaseModel):
    symbols: List[str]
    allocation: List[AllocationItem]
    expected_return: float
    risk: float
    sharpe_ratio: float
    optimization_successful: bool

    current_price: Optional[float] = None
    current_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    class Config:
        from_attributes = True

# Holding schema
class HoldingBase(BaseModel):
    symbol: str
    quantity: float
    average_price: float

class HoldingCreate(HoldingBase):
    portfolioId: int

class HoldingUpdate(BaseModel):
    quantity: Optional[float] = None
    average_price: Optional[float] = None

class Holding(HoldingBase):
    id: int
    portfolio_id: int
    created_at: datetime
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    class Config:
        from_attributes = True

class PortfolioDetail(Portfolio):
    holdings: List[Holding]
    total_value: float
    total_investment: float
    total_pnl: float
    total_pnl_percent: float

# Watchlist schemas
class WatchListItem(BaseModel):
    stock_symbol: str

class WatchList(BaseModel):
    id: int
    user_id: int
    stock: Stock
    created_at: datetime
    
    class Config:
        from_attributes = True

# Aggregated Portfolio Holding schema
class PortfolioHolding(BaseModel):
    symbol: str
    name: str
    quantity: float
    average_price: float
    current_price: float
    current_value: float
    investment_value: float
    pnl: float
    pnl_percent: float
    portfolio_name: str
    portfolio_id: int

# Market Mover schema
class MarketMover(BaseModel):
    rank: int
    symbol: str
    name: str
    current_price: float
    change_percent: float
    volume: int
    
    class Config:
        from_attributes = True

# API Response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

# Investment Profile schemas
class InvestmentProfileBase(BaseModel):
    investment_amount: float
    risk_level: str  # 'low', 'medium', 'high'
    timeline: str    # 'short', 'long'
    investment_goals: Optional[str] = None
    monthly_income: Optional[float] = None
    age: Optional[int] = None

class InvestmentProfileCreate(InvestmentProfileBase):
    pass

class InvestmentProfileUpdate(BaseModel):
    investment_amount: Optional[float] = None
    risk_level: Optional[str] = None
    timeline: Optional[str] = None
    investment_goals: Optional[str] = None
    monthly_income: Optional[float] = None
    age: Optional[int] = None

class InvestmentProfile(InvestmentProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Indian Stock schemas
class IndianStockBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    market_cap_category: Optional[str] = None  # 'large', 'mid', 'small'
    current_price: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    is_nifty50: Optional[bool] = False
    is_nifty100: Optional[bool] = False
    is_nifty500: Optional[bool] = False

class IndianStock(IndianStockBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Stock price with INR formatting
class IndianStockPrice(BaseModel):
    symbol: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    company_name: str
    currency: str = "INR"  # Always INR for Indian stocks
    formatted_price: str  # Price formatted as ₹X,XXX.XX
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

# User Recommendation schemas
class UserRecommendationBase(BaseModel):
    stock_symbol: str
    recommendation_type: str  # 'buy', 'hold', 'sell'
    confidence_score: Optional[float] = None
    reason: Optional[str] = None
    target_price: Optional[float] = None

class UserRecommendation(UserRecommendationBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI Chat with context schemas
class PersonalizedChatMessage(BaseModel):
    message: str
    include_profile: bool = True  # Include user investment profile in context

class PersonalizedChatResponse(BaseModel):
    message: str
    response: str
    recommendations: Optional[List[UserRecommendationBase]] = None
    timestamp: str
    user_profile_considered: bool = False

# Screener.in clone schemas
class CompanyFinancialsBase(BaseModel):
    symbol: str
    year: int
    quarter: Optional[int] = None
    revenue: Optional[float] = None
    operating_profit: Optional[float] = None
    net_profit: Optional[float] = None
    eps: Optional[float] = None
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    shareholders_equity: Optional[float] = None
    debt: Optional[float] = None
    cash: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    market_cap: Optional[float] = None
    book_value: Optional[float] = None

class CompanyFinancials(CompanyFinancialsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ScreenerFilters(BaseModel):
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    market_cap_category: Optional[List[str]] = None
    pe_ratio_min: Optional[float] = None
    pe_ratio_max: Optional[float] = None
    pb_ratio_min: Optional[float] = None
    pb_ratio_max: Optional[float] = None
    roe_min: Optional[float] = None
    roe_max: Optional[float] = None
    net_margin_min: Optional[float] = None
    net_margin_max: Optional[float] = None
    revenue_growth_1y_min: Optional[float] = None
    profit_growth_1y_min: Optional[float] = None
    debt_to_equity_max: Optional[float] = None
    current_ratio_min: Optional[float] = None
    dividend_yield_min: Optional[float] = None
    sectors: Optional[List[str]] = None
    industries: Optional[List[str]] = None
    only_nifty50: Optional[bool] = False
    only_nifty100: Optional[bool] = False
    only_nifty500: Optional[bool] = False
    sort_by: Optional[str] = "market_cap"
    sort_order: Optional[str] = "desc"
    page: Optional[int] = 1
    limit: Optional[int] = 50

class StockScreenerData(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_category: Optional[str] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    dividend_yield: Optional[float] = None
    revenue_growth_1y: Optional[float] = None
    profit_growth_1y: Optional[float] = None
    price_change_1y: Optional[float] = None
    screener_score: Optional[float] = None

class ScreenerResults(BaseModel):
    stocks: List[StockScreenerData]
    total_count: int
    page: int
    limit: int
    total_pages: int
    filters_applied: ScreenerFilters


# Enhanced Profile System Schemas

