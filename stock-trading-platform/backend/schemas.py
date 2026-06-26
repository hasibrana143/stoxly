from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    captcha_token: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    captcha_token: Optional[str] = None

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

class MarketMover(BaseModel):
    rank: int
    symbol: str
    name: str
    current_price: float
    change_percent: float
    volume: int

    class Config:
        from_attributes = True

class OptimizationRequest(BaseModel):
    symbols: List[str]
    risk_tolerance: Optional[str] = "moderate"
    investment_horizon: Optional[str] = "medium"

class IndianStockPrice(BaseModel):
    symbol: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    company_name: str
    currency: str = "INR"
    formatted_price: str
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

class InvestmentProfileBase(BaseModel):
    investment_amount: float
    risk_level: str
    timeline: str
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

class UserRecommendationBase(BaseModel):
    stock_symbol: str
    recommendation_type: str
    confidence_score: Optional[float] = None
    reason: Optional[str] = None
    target_price: Optional[float] = None

class PersonalizedChatMessage(BaseModel):
    message: str
    include_profile: bool = True

class PersonalizedChatResponse(BaseModel):
    message: str
    response: str
    recommendations: Optional[List[UserRecommendationBase]] = None
    timestamp: str
    user_profile_considered: bool = False

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
