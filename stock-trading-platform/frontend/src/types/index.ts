export interface User {
  id: number;
  username: string;
  email: string;
}

export interface Stock {
  symbol: string;
  name: string;
  exchange: string;
  sector: string;
  market_cap_category: string;
  current_price: number;
  change: number;
  change_percent: number;
  volume: number;
  market_cap: number;
  is_nifty50?: boolean;
  is_nifty100?: boolean;
}

export interface StockDetail extends Stock {
  previous_close: number;
  company_name: string;
  pe_ratio: number;
  roe: number;
  roce: number;
  book_value: number;
  dividend_yield: number;
  price_change_1w: number;
  price_change_1m: number;
  price_change_3m: number;
  price_change_6m: number;
  price_change_1y: number;
  high_52w: number;
  low_52w: number;
}

export interface Portfolio {
  id: number;
  name: string;
  description?: string;
  created_at: string;
}

export interface Holding {
  id: number;
  portfolio_id: number;
  symbol: string;
  name: string;
  quantity: number;
  average_price: number;
  current_price: number;
  current_value: number;
  investment_value: number;
  pnl: number;
  pnl_percent: number;
  portfolio_name?: string;
}

export interface WatchlistItem {
  id: number;
  stock_id: number;
  symbol: string;
  name: string;
  current_price: number;
  change: number;
  change_percent: number;
  market_cap: number;
  pe_ratio: number;
}

export interface MarketMover {
  rank: number;
  symbol: string;
  name: string;
  current_price: number;
  change_percent: number;
  volume: number;
}

export interface InvestmentProfile {
  id: number;
  user_id: number;
  investment_amount: number;
  risk_level: string;
  timeline: string;
  investment_goals: string;
  monthly_income?: number;
  age?: number;
}

export interface ChatMessage {
  message: string;
  response: string;
  recommendations?: any[];
  timestamp: string;
  user_profile_considered?: boolean;
}

export interface PriceUpdate {
  symbol: string;
  price: number;
  change: number;
  change_percent: number;
}

export interface ApiError {
  detail: string;
}
