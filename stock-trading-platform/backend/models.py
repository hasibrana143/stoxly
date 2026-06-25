from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base, engine

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    investment_profile = relationship("InvestmentProfile", back_populates="user", uselist=False)

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    holdings = relationship("Holding", back_populates="portfolio")

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    exchange = Column(String(50))
    sector = Column(String(100))
    market_cap = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    transactions = relationship("Transaction", back_populates="stock")

class Holding(Base):
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    average_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    transaction_type = Column(String(10), nullable=False)  # 'BUY' or 'SELL'
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    stock = relationship("Stock", back_populates="transactions")

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

class WatchList(Base):
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    stock = relationship("Stock")

class InvestmentProfile(Base):
    __tablename__ = "investment_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investment_amount = Column(Float, nullable=False)  # Investment amount in INR
    risk_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high'
    timeline = Column(String(20), nullable=False)  # 'short', 'long'
    investment_goals = Column(Text)
    monthly_income = Column(Float)
    age = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="investment_profile")

class IndianStock(Base):
    __tablename__ = "indian_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False)  # e.g., 'TCS.NS'
    name = Column(String(200), nullable=False)  # e.g., 'Tata Consultancy Services'
    sector = Column(String(100))  # e.g., 'Information Technology'
    market_cap_category = Column(String(20))  # 'large', 'mid', 'small'
    current_price = Column(Float)
    pe_ratio = Column(Float)
    dividend_yield = Column(Float)
    fifty_two_week_high = Column(Float)
    fifty_two_week_low = Column(Float)
    is_nifty50 = Column(Boolean, default=False)
    is_nifty100 = Column(Boolean, default=False)
    is_nifty500 = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserRecommendation(Base):
    __tablename__ = "user_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_symbol = Column(String(20), nullable=False)
    recommendation_type = Column(String(20), nullable=False)  # 'buy', 'hold', 'sell'
    confidence_score = Column(Float)  # 0.0 to 1.0
    reason = Column(Text)
    target_price = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")

# Screener.in clone models
class CompanyFinancials(Base):
    __tablename__ = "company_financials"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    year = Column(Integer, nullable=False)
    quarter = Column(Integer)  # 1, 2, 3, 4 or None for annual
    
    # Income Statement
    revenue = Column(Float)  # in crores
    operating_profit = Column(Float)
    net_profit = Column(Float)
    eps = Column(Float)  # Earnings per share
    
    # Balance Sheet
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    shareholders_equity = Column(Float)
    debt = Column(Float)
    cash = Column(Float)
    
    # Ratios
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    roe = Column(Float)  # Return on Equity
    roa = Column(Float)  # Return on Assets
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    dividend_yield = Column(Float)
    
    # Market Data
    market_cap = Column(Float)
    book_value = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class StockScreener(Base):
    __tablename__ = "stock_screener"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    name = Column(String(200), nullable=False)
    sector = Column(String(100))
    industry = Column(String(100))
    
    # Current Market Data
    current_price = Column(Float)
    market_cap = Column(Float)  # in crores
    market_cap_category = Column(String(20))  # large, mid, small
    
    # Valuation Ratios
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    ps_ratio = Column(Float)  # Price to Sales
    ev_ebitda = Column(Float)
    
    # Profitability Ratios
    roe = Column(Float)
    roa = Column(Float)
    roic = Column(Float)  # Return on Invested Capital
    gross_margin = Column(Float)
    operating_margin = Column(Float)
    net_margin = Column(Float)
    
    # Financial Health
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    interest_coverage = Column(Float)
    
    # Growth Metrics
    revenue_growth_1y = Column(Float)
    revenue_growth_3y = Column(Float)
    profit_growth_1y = Column(Float)
    profit_growth_3y = Column(Float)
    
    # Dividend
    dividend_yield = Column(Float)
    dividend_payout_ratio = Column(Float)
    
    # Price Performance
    price_change_1d = Column(Float)
    price_change_1w = Column(Float)
    price_change_1m = Column(Float)
    price_change_3m = Column(Float)
    price_change_6m = Column(Float)
    price_change_1y = Column(Float)
    
    # 52 Week Range
    week_52_high = Column(Float)
    week_52_low = Column(Float)
    
    # Volume
    avg_volume = Column(Float)
    volume = Column(Float)
    
    # Index Membership
    is_nifty50 = Column(Boolean, default=False)
    is_nifty100 = Column(Boolean, default=False)
    is_nifty500 = Column(Boolean, default=False)
    
    # Screener Score (custom ranking)
    screener_score = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SectorAnalysis(Base):
    __tablename__ = "sector_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(100), nullable=False)
    
    # Sector Metrics
    avg_pe_ratio = Column(Float)
    avg_pb_ratio = Column(Float)
    avg_roe = Column(Float)
    avg_debt_to_equity = Column(Float)
    avg_dividend_yield = Column(Float)
    
    # Performance
    sector_return_1m = Column(Float)
    sector_return_3m = Column(Float)
    sector_return_6m = Column(Float)
    sector_return_1y = Column(Float)
    
    total_market_cap = Column(Float)
    stock_count = Column(Integer)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserScreenerFilter(Base):
    __tablename__ = "user_screener_filters"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filter_name = Column(String(100), nullable=False)
    filter_criteria = Column(Text, nullable=False)  # JSON string of filter criteria
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")


# Enhanced Profile System Models


class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String(200))
    profile_picture_url = Column(String(500))
    phone_number = Column(String(20))
    date_of_birth = Column(DateTime)
    location = Column(String(100))
    preferred_language = Column(String(10), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="profile")


class InvestmentPreferences(Base):
    __tablename__ = "investment_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    investment_style = Column(String(50))  # value, growth, dividend, momentum, hybrid
    risk_tolerance = Column(String(50))  # conservative, moderate, aggressive
    investment_goals = Column(Text)  # JSON array
    preferred_sectors = Column(Text)  # JSON array
    investment_horizon = Column(String(50))
    portfolio_size_range = Column(String(50))
    trading_experience = Column(String(50))  # beginner, intermediate, advanced, expert
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="investment_preferences")


class NotificationSettings(Base):
    __tablename__ = "notification_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    price_alerts_enabled = Column(Boolean, default=True)
    price_alert_threshold = Column(Float, default=5.0)
    news_alerts_enabled = Column(Boolean, default=True)
    earnings_alerts_enabled = Column(Boolean, default=True)
    dividend_alerts_enabled = Column(Boolean, default=True)
    portfolio_updates_frequency = Column(String(20), default="daily")  # daily, weekly, monthly
    market_reminders_enabled = Column(Boolean, default=False)
    email_notifications = Column(Text)  # JSON
    sms_notifications = Column(Text)  # JSON
    push_notifications = Column(Text)  # JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="notification_settings")


class DisplayPreferences(Base):
    __tablename__ = "display_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    theme = Column(String(20), default="light")  # light, dark, auto
    default_currency = Column(String(10), default="INR")
    number_format = Column(String(20), default="indian")  # indian, international
    date_format = Column(String(20), default="DD/MM/YYYY")
    chart_type = Column(String(20), default="candlestick")
    default_time_period = Column(String(10), default="1M")
    stocks_per_page = Column(Integer, default=25)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="display_preferences")


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(500), unique=True, nullable=False)
    device_info = Column(String(200))
    browser = Column(String(100))
    ip_address = Column(String(50))
    location = Column(String(100))
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    user = relationship("User", backref="sessions")


class LoginHistory(Base):
    __tablename__ = "login_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50))
    device_info = Column(String(200))
    browser = Column(String(100))
    location = Column(String(100))
    success = Column(Boolean, default=True)
    
    # Relationship
    user = relationship("User", backref="login_history")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    plan_type = Column(String(20), default="free")  # free, premium, pro
    status = Column(String(20), default="active")  # active, expired, cancelled
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True))
    auto_renew = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="subscription")


class PaymentHistory(Base):
    __tablename__ = "payment_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    plan_type = Column(String(20), nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String(50))
    invoice_url = Column(String(500))
    status = Column(String(20), default="completed")  # completed, pending, failed
    
    # Relationship
    user = relationship("User", backref="payment_history")


class UserActivity(Base):
    __tablename__ = "user_activity"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    total_searches = Column(Integer, default=0)
    most_viewed_stocks = Column(Text)  # JSON array
    recently_viewed_stocks = Column(Text)  # JSON array
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    user = relationship("User", backref="activity")


# Create all tables function
def create_tables():
    Base.metadata.create_all(bind=engine)
