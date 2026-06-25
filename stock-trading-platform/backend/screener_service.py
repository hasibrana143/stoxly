import random
import math
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from models import StockScreener, CompanyFinancials, SectorAnalysis
from schemas import ScreenerFilters, ScreenerResults, StockScreenerData
from stock_data_list import INDIAN_STOCKS_DATABASE

class ScreenerService:
    """Service class for stock screening functionality similar to screener.in"""
    
    def __init__(self):
        self.mock_data = self._generate_mock_screener_data()
    
    def _generate_mock_screener_data(self) -> List[Dict]:
        """Generate comprehensive mock data for Indian stocks with financial metrics"""
        screener_data = []
        
        for stock_info in INDIAN_STOCKS_DATABASE:
            symbol = stock_info["symbol"]
            # Generate realistic financial metrics
            market_cap = self._get_market_cap_value(stock_info["market_cap_category"])
            current_price = random.uniform(50, 5000)
            
            # Generate ratios based on sector and market cap
            pe_ratio = self._generate_pe_ratio(stock_info["sector"], stock_info["market_cap_category"])
            pb_ratio = random.uniform(0.5, 8.0)
            roe = random.uniform(5, 35)
            roce = roe * random.uniform(0.9, 1.3)  # ROCE typically correlates with ROE
            debt_to_equity = random.uniform(0.1, 2.5)
            book_value = current_price / pb_ratio if pb_ratio > 0 else 0
            
            # Growth metrics
            revenue_growth_1y = random.uniform(-20, 50)
            profit_growth_1y = random.uniform(-30, 80)
            
            # Price performance
            price_change_1y = random.uniform(-60, 150)
            
            # Calculate screener score (0-100)
            screener_score = self._calculate_screener_score({
                'pe_ratio': pe_ratio,
                'roe': roe,
                'debt_to_equity': debt_to_equity,
                'revenue_growth_1y': revenue_growth_1y,
                'profit_growth_1y': profit_growth_1y
            })
            
            screener_data.append({
                'symbol': symbol,
                'name': stock_info['name'],
                'sector': stock_info['sector'],
                'industry': stock_info.get('industry', stock_info['sector']),
                'current_price': round(current_price, 2),
                'market_cap': market_cap,
                'market_cap_category': stock_info['market_cap_category'],
                'pe_ratio': round(pe_ratio, 2) if pe_ratio else None,
                'pb_ratio': round(pb_ratio, 2),
                'ps_ratio': round(random.uniform(0.5, 15.0), 2),
                'ev_ebitda': round(random.uniform(5, 25), 2),
                'roe': round(roe, 2),
                'roce': round(roce, 2),
                'book_value': round(book_value, 2),
                'roa': round(random.uniform(2, 20), 2),
                'roic': round(random.uniform(8, 30), 2),
                'gross_margin': round(random.uniform(15, 80), 2),
                'operating_margin': round(random.uniform(5, 40), 2),
                'net_margin': round(random.uniform(2, 25), 2),
                'debt_to_equity': round(debt_to_equity, 2),
                'current_ratio': round(random.uniform(0.8, 4.0), 2),
                'quick_ratio': round(random.uniform(0.5, 3.0), 2),
                'interest_coverage': round(random.uniform(2, 50), 2),
                'revenue_growth_1y': round(revenue_growth_1y, 2),
                'revenue_growth_3y': round(random.uniform(-10, 30), 2),
                'profit_growth_1y': round(profit_growth_1y, 2),
                'profit_growth_3y': round(random.uniform(-15, 40), 2),
                'dividend_yield': round(random.uniform(0, 8), 2),
                'dividend_payout_ratio': round(random.uniform(10, 80), 2),
                'price_change_1d': round(random.uniform(-5, 5), 2),
                'price_change_1w': round(random.uniform(-10, 10), 2),
                'price_change_1m': round(random.uniform(-20, 20), 2),
                'price_change_3m': round(random.uniform(-30, 30), 2),
                'price_change_6m': round(random.uniform(-40, 40), 2),
                'price_change_1y': round(price_change_1y, 2),
                'week_52_high': round(current_price * random.uniform(1.0, 1.8), 2),
                'week_52_low': round(current_price * random.uniform(0.4, 0.9), 2),
                'avg_volume': random.randint(10000, 10000000),
                'volume': random.randint(5000, 15000000),
                'is_nifty50': stock_info.get('is_nifty50', False),
                'is_nifty100': stock_info.get('is_nifty100', False),
                'is_nifty500': stock_info.get('is_nifty500', False),
                'screener_score': round(screener_score, 2)
            })
        
        return screener_data
    
    def _get_market_cap_value(self, category: str) -> float:
        """Get market cap value based on category"""
        if category == "large":
            return random.uniform(20000, 500000)  # 20k to 5L crores
        elif category == "mid":
            return random.uniform(5000, 20000)   # 5k to 20k crores
        else:  # small
            return random.uniform(500, 5000)     # 500 to 5k crores
    
    def _generate_pe_ratio(self, sector: str, market_cap_category: str) -> Optional[float]:
        """Generate realistic P/E ratios based on sector"""
        sector_pe_ranges = {
            "Information Technology": (15, 35),
            "Banking": (8, 20),
            "Pharmaceuticals": (12, 30),
            "Automobiles": (10, 25),
            "FMCG": (20, 50),
            "Energy": (5, 15),
            "Metals": (5, 20),
            "Telecommunications": (10, 25),
            "Real Estate": (8, 30),
            "Textiles": (8, 20)
        }
        
        pe_range = sector_pe_ranges.get(sector, (8, 25))
        
        # Some stocks might not have P/E (loss-making)
        if random.random() < 0.1:  # 10% chance of no P/E
            return None
        
        return random.uniform(pe_range[0], pe_range[1])
    
    def _calculate_screener_score(self, metrics: Dict) -> float:
        """Calculate a composite screener score (0-100)"""
        score = 50  # Base score
        
        # P/E ratio scoring (lower is better)
        if metrics.get('pe_ratio'):
            if metrics['pe_ratio'] < 15:
                score += 15
            elif metrics['pe_ratio'] < 25:
                score += 10
            elif metrics['pe_ratio'] > 40:
                score -= 10
        
        # ROE scoring (higher is better)
        if metrics['roe'] > 20:
            score += 15
        elif metrics['roe'] > 15:
            score += 10
        elif metrics['roe'] < 10:
            score -= 10
        
        # Debt to equity (lower is better)
        if metrics['debt_to_equity'] < 0.5:
            score += 10
        elif metrics['debt_to_equity'] > 1.5:
            score -= 10
        
        # Growth scoring
        if metrics['revenue_growth_1y'] > 20:
            score += 10
        elif metrics['revenue_growth_1y'] < 0:
            score -= 5
        
        if metrics['profit_growth_1y'] > 25:
            score += 10
        elif metrics['profit_growth_1y'] < 0:
            score -= 10
        
        return max(0, min(100, score))
    
    def screen_stocks(self, filters: ScreenerFilters) -> ScreenerResults:
        """Screen stocks based on provided filters"""
        filtered_stocks = self.mock_data.copy()
        
        # Apply filters
        if filters.market_cap_min:
            filtered_stocks = [s for s in filtered_stocks if s['market_cap'] >= filters.market_cap_min]
        
        if filters.market_cap_max:
            filtered_stocks = [s for s in filtered_stocks if s['market_cap'] <= filters.market_cap_max]
        
        if filters.market_cap_category:
            filtered_stocks = [s for s in filtered_stocks if s['market_cap_category'] in filters.market_cap_category]
        
        if filters.pe_ratio_min:
            filtered_stocks = [s for s in filtered_stocks if s['pe_ratio'] and s['pe_ratio'] >= filters.pe_ratio_min]
        
        if filters.pe_ratio_max:
            filtered_stocks = [s for s in filtered_stocks if s['pe_ratio'] and s['pe_ratio'] <= filters.pe_ratio_max]
        
        if filters.pb_ratio_min:
            filtered_stocks = [s for s in filtered_stocks if s['pb_ratio'] >= filters.pb_ratio_min]
        
        if filters.pb_ratio_max:
            filtered_stocks = [s for s in filtered_stocks if s['pb_ratio'] <= filters.pb_ratio_max]
        
        if filters.roe_min:
            filtered_stocks = [s for s in filtered_stocks if s['roe'] >= filters.roe_min]
        
        if filters.roe_max:
            filtered_stocks = [s for s in filtered_stocks if s['roe'] <= filters.roe_max]
        
        if filters.net_margin_min:
            filtered_stocks = [s for s in filtered_stocks if s['net_margin'] >= filters.net_margin_min]
        
        if filters.net_margin_max:
            filtered_stocks = [s for s in filtered_stocks if s['net_margin'] <= filters.net_margin_max]
        
        if filters.revenue_growth_1y_min:
            filtered_stocks = [s for s in filtered_stocks if s['revenue_growth_1y'] >= filters.revenue_growth_1y_min]
        
        if filters.profit_growth_1y_min:
            filtered_stocks = [s for s in filtered_stocks if s['profit_growth_1y'] >= filters.profit_growth_1y_min]
        
        if filters.debt_to_equity_max:
            filtered_stocks = [s for s in filtered_stocks if s['debt_to_equity'] <= filters.debt_to_equity_max]
        
        if filters.current_ratio_min:
            filtered_stocks = [s for s in filtered_stocks if s['current_ratio'] >= filters.current_ratio_min]
        
        if filters.dividend_yield_min:
            filtered_stocks = [s for s in filtered_stocks if s['dividend_yield'] >= filters.dividend_yield_min]
        
        if filters.sectors:
            filtered_stocks = [s for s in filtered_stocks if s['sector'] in filters.sectors]
        
        if filters.industries:
            filtered_stocks = [s for s in filtered_stocks if s['industry'] in filters.industries]
        
        if filters.only_nifty50:
            filtered_stocks = [s for s in filtered_stocks if s['is_nifty50']]
        
        if filters.only_nifty100:
            filtered_stocks = [s for s in filtered_stocks if s['is_nifty100']]
        
        if filters.only_nifty500:
            filtered_stocks = [s for s in filtered_stocks if s['is_nifty500']]
        
        # Sort results
        sort_key = filters.sort_by or "market_cap"
        reverse = filters.sort_order == "desc"
        
        try:
            filtered_stocks.sort(
                key=lambda x: x.get(sort_key, 0) or 0,
                reverse=reverse
            )
        except (KeyError, TypeError):
            # Fallback to market cap sorting
            filtered_stocks.sort(key=lambda x: x['market_cap'], reverse=True)
        
        # Pagination
        total_count = len(filtered_stocks)
        page = filters.page or 1
        limit = min(filters.limit or 50, 100)  # Max 100 results per page
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        
        paginated_stocks = filtered_stocks[start_idx:end_idx]
        
        # Convert to schema format
        stock_results = [
            StockScreenerData(
                symbol=stock['symbol'],
                name=stock['name'],
                sector=stock['sector'],
                industry=stock['industry'],
                current_price=stock['current_price'],
                market_cap=stock['market_cap'],
                market_cap_category=stock['market_cap_category'],
                pe_ratio=stock['pe_ratio'],
                pb_ratio=stock['pb_ratio'],
                roe=stock['roe'],
                debt_to_equity=stock['debt_to_equity'],
                dividend_yield=stock['dividend_yield'],
                revenue_growth_1y=stock['revenue_growth_1y'],
                profit_growth_1y=stock['profit_growth_1y'],
                price_change_1y=stock['price_change_1y'],
                screener_score=stock['screener_score']
            )
            for stock in paginated_stocks
        ]
        
        return ScreenerResults(
            stocks=stock_results,
            total_count=total_count,
            page=page,
            limit=limit,
            total_pages=math.ceil(total_count / limit),
            filters_applied=filters
        )
    
    def get_stock_details(self, symbol: str) -> Optional[Dict]:
        """Get detailed information for a specific stock"""
        stock_data = next((s for s in self.mock_data if s['symbol'] == symbol), None)
        if not stock_data:
            return None
        
        # Add additional details for company profile
        stock_data['description'] = f"{stock_data['name']} is a leading company in the {stock_data['sector']} sector."
        stock_data['website'] = f"https://www.{symbol.lower().replace('.ns', '').replace('.bo', '')}.com"
        stock_data['employees'] = random.randint(1000, 100000)
        stock_data['founded_year'] = random.randint(1950, 2010)
        stock_data['headquarters'] = random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'])
        
        return stock_data

    def get_profit_loss(self, symbol: str) -> List[Dict]:
        results = []
        stock = next((s for s in self.mock_data if s['symbol'] == symbol), None)
        if not stock:
            return results
        base_sales = stock['market_cap'] / 120
        now_year = datetime.now().year
        for i in range(8):
            year = now_year - (7 - i)
            sales = max(200.0, base_sales * (1 + random.uniform(-0.1, 0.2)) * (1 + i * random.uniform(0.02, 0.08)))
            expenses = sales * random.uniform(0.6, 0.85)
            op_profit = sales - expenses
            other_income = sales * random.uniform(0.008, 0.02)
            interest = sales * random.uniform(0.004, 0.015)
            depreciation = sales * random.uniform(0.008, 0.02)
            pbt = op_profit + other_income - interest - depreciation
            tax = pbt * random.uniform(0.2, 0.3)
            net_profit = pbt - tax
            eps = max(0.1, net_profit / random.uniform(70, 180))
            results.append({
                'year': year,
                'sales': round(sales),
                'operating_profit': round(op_profit),
                'other_income': round(other_income),
                'interest': round(interest),
                'depreciation': round(depreciation),
                'pbt': round(pbt),
                'net_profit': round(net_profit),
                'eps': round(eps, 2)
            })
        return results

    def get_balance_sheet(self, symbol: str) -> List[Dict]:
        results = []
        stock = next((s for s in self.mock_data if s['symbol'] == symbol), None)
        if not stock:
            return results
        base_assets = stock['market_cap'] * random.uniform(1.5, 3.5)
        now_year = datetime.now().year
        for i in range(8):
            year = now_year - (7 - i)
            assets = base_assets * (1 + i * random.uniform(0.03, 0.1))
            equity = assets * random.uniform(0.35, 0.6)
            debt = assets * random.uniform(0.1, 0.4)
            liabilities = max(assets - equity, debt + assets * random.uniform(0.05, 0.2))
            cash = assets * random.uniform(0.02, 0.1)
            results.append({
                'year': year,
                'total_assets': round(assets),
                'total_liabilities': round(liabilities),
                'shareholders_equity': round(equity),
                'debt': round(debt),
                'cash': round(cash)
            })
        return results

    def get_cash_flow(self, symbol: str) -> List[Dict]:
        results = []
        stock = next((s for s in self.mock_data if s['symbol'] == symbol), None)
        if not stock:
            return results
        base_sales = stock['market_cap'] / 120
        now_year = datetime.now().year
        for i in range(8):
            year = now_year - (7 - i)
            operating_cash_flow = max(100.0, base_sales * (1 + random.uniform(-0.1, 0.2)) * (1 + i * random.uniform(0.02, 0.08)))
            investing_cash_flow = -abs(operating_cash_flow * random.uniform(0.1, 0.4))
            financing_cash_flow = operating_cash_flow * random.uniform(-0.2, 0.2)
            free_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
            results.append({
                'year': year,
                'operating_cash_flow': round(operating_cash_flow),
                'investing_cash_flow': round(investing_cash_flow),
                'financing_cash_flow': round(financing_cash_flow),
                'free_cash_flow': round(free_cash_flow)
            })
        return results
    
    def get_sector_analysis(self) -> List[Dict]:
        """Get sector-wise analysis"""
        sectors = {}
        
        for stock in self.mock_data:
            sector = stock['sector']
            if sector not in sectors:
                sectors[sector] = {
                    'stocks': [],
                    'total_market_cap': 0
                }
            sectors[sector]['stocks'].append(stock)
            sectors[sector]['total_market_cap'] += stock['market_cap']
        
        sector_analysis = []
        for sector, data in sectors.items():
            stocks = data['stocks']
            stock_count = len(stocks)
            
            # Calculate averages
            avg_pe = sum(s['pe_ratio'] for s in stocks if s['pe_ratio']) / len([s for s in stocks if s['pe_ratio']])
            avg_pb = sum(s['pb_ratio'] for s in stocks) / stock_count
            avg_roe = sum(s['roe'] for s in stocks) / stock_count
            avg_debt_to_equity = sum(s['debt_to_equity'] for s in stocks) / stock_count
            avg_dividend_yield = sum(s['dividend_yield'] for s in stocks) / stock_count
            
            sector_analysis.append({
                'sector': sector,
                'avg_pe_ratio': round(avg_pe, 2),
                'avg_pb_ratio': round(avg_pb, 2),
                'avg_roe': round(avg_roe, 2),
                'avg_debt_to_equity': round(avg_debt_to_equity, 2),
                'avg_dividend_yield': round(avg_dividend_yield, 2),
                'sector_return_1m': round(random.uniform(-10, 15), 2),
                'sector_return_3m': round(random.uniform(-20, 25), 2),
                'sector_return_6m': round(random.uniform(-30, 35), 2),
                'sector_return_1y': round(random.uniform(-40, 60), 2),
                'total_market_cap': round(data['total_market_cap'], 2),
                'stock_count': stock_count
            })
        
        return sorted(sector_analysis, key=lambda x: x['total_market_cap'], reverse=True)
    
    def get_peer_comparison(self, symbol: str) -> Dict:
        """Get peer comparison for a stock"""
        stock = self.get_stock_details(symbol)
        if not stock:
            return {}
        
        # Find peers in the same sector
        peers = [s for s in self.mock_data 
                if s['sector'] == stock['sector'] and s['symbol'] != symbol]
        
        # Sort by market cap and take top 10
        peers.sort(key=lambda x: x['market_cap'], reverse=True)
        peers = peers[:10]
        
        return {
            'symbol': symbol,
            'stock': stock,
            'peers': peers,
            'sector': stock['sector']
        }
    
    def get_top_stocks(self, criteria: str = "market_cap", limit: int = 20) -> List[Dict]:
        """Get top stocks based on different criteria"""
        if criteria == "gainers_1d":
            sorted_stocks = sorted(self.mock_data, key=lambda x: x['price_change_1d'], reverse=True)
        elif criteria == "losers_1d":
            sorted_stocks = sorted(self.mock_data, key=lambda x: x['price_change_1d'])
        elif criteria == "volume":
            sorted_stocks = sorted(self.mock_data, key=lambda x: x['volume'], reverse=True)
        elif criteria == "screener_score":
            sorted_stocks = sorted(self.mock_data, key=lambda x: x['screener_score'], reverse=True)
        elif criteria == "dividend_yield":
            sorted_stocks = sorted(self.mock_data, key=lambda x: x['dividend_yield'], reverse=True)
        else:  # market_cap
            sorted_stocks = sorted(self.mock_data, key=lambda x: x['market_cap'], reverse=True)
        
        return sorted_stocks[:limit]

    def get_quarterly_results(self, symbol: str) -> List[Dict]:
        quarters = []
        stock = next((s for s in self.mock_data if s['symbol'] == symbol), None)
        if not stock:
            return quarters
        base_sales = stock['market_cap'] / 100
        now = datetime.now()
        for i in range(12):
            q_date = now - timedelta(days=90 * (11 - i))
            sales = max(50.0, base_sales * random.uniform(0.8, 1.2))
            expenses = sales * random.uniform(0.6, 0.85)
            op_profit = sales - expenses
            opm = (op_profit / sales) * 100
            other_income = sales * random.uniform(0.01, 0.03)
            interest = sales * random.uniform(0.005, 0.02)
            depreciation = sales * random.uniform(0.01, 0.03)
            pbt = op_profit + other_income - interest - depreciation
            tax_pct = random.uniform(20, 30)
            tax = pbt * (tax_pct / 100)
            net_profit = pbt - tax
            eps = max(0.1, net_profit / random.uniform(50, 200))
            quarters.append({
                'period': q_date.strftime('%b %Y'),
                'sales': round(sales),
                'expenses': round(expenses),
                'operating_profit': round(op_profit),
                'opm_percent': round(opm, 1),
                'other_income': round(other_income),
                'interest': round(interest),
                'depreciation': round(depreciation),
                'pbt': round(pbt),
                'tax_percent': round(tax_pct, 0),
                'net_profit': round(net_profit),
                'eps': round(eps, 2)
            })
        return quarters

# Global instance
screener_service = ScreenerService()