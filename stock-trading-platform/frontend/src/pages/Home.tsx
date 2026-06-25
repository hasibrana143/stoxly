import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useGetAllIndianStocksQuery } from '../services/api';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/solid';

// Types for stock data
interface StockData {
  symbol: string;
  name: string;
  current_price: number;
  formatted_price: string;
  change: number;
  change_percent: number;
  sector: string;
  market_cap_category: string;
}

const Home: React.FC = () => {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();
  const { data: initialStocks, isLoading } = useGetAllIndianStocksQuery(undefined);
  const [stocks, setStocks] = useState<StockData[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  // Initialize stocks from API
  useEffect(() => {
    if (initialStocks?.stocks) {
      setStocks(initialStocks.stocks as any);
    }
  }, [initialStocks]);

  // WebSocket connection for live updates
  useEffect(() => {
    let active = true;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let ws: WebSocket | null = null;

    const applyUpdates = (updates: any[]) => {
      if (!Array.isArray(updates)) return;
      setStocks(prevStocks => {
        const newStocks = [...prevStocks];
        updates.forEach((update: any) => {
          const index = newStocks.findIndex(s => s.symbol === update.symbol);
          if (index !== -1) {
            newStocks[index] = {
              ...newStocks[index],
              current_price: update.price ?? update.current_price,
              formatted_price: `₹${(update.price ?? update.current_price).toFixed(2)}`,
              change_percent: update.change_percent
            };
          }
        });
        return newStocks;
      });
    };

    const connectWebSocket = () => {
      if (!active) return;

      ws = new WebSocket('ws://localhost:8000/ws/stocks');
      wsRef.current = ws;

      ws.onopen = () => {
        if (active) {
          console.log('Connected to stock updates');
        }
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'PRICE_UPDATE') {
            applyUpdates(message.data);
          } else if (Array.isArray(message)) {
            applyUpdates(message);
          }
        } catch (e) {
          console.error('Error parsing websocket message', e);
        }
      };

      ws.onclose = () => {
        ws = null;
        wsRef.current = null;
        if (active) {
          reconnectTimer = setTimeout(connectWebSocket, 5000);
        }
      };

      ws.onerror = () => {
        ws?.close();
      };
    };

    connectWebSocket();

    return () => {
      active = false;
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
      if (ws) {
        ws.onclose = null;
        ws.close();
      }
      wsRef.current = null;
    };
  }, []);

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/stocks');
  };

  const [pennyLimit, setPennyLimit] = useState(6);
  const [mediumLimit, setMediumLimit] = useState(6);

  // Categorize stocks
  const pennyStocksAll = stocks.filter(s => s.current_price < 50);
  const mediumStocksAll = stocks.filter(s => s.market_cap_category === 'mid' || (s.current_price >= 50 && s.current_price < 1000));

  const pennyStocks = pennyStocksAll.slice(0, pennyLimit);
  const mediumStocks = mediumStocksAll.slice(0, mediumLimit);
  const topGainers = [...stocks].sort((a, b) => b.change_percent - a.change_percent).slice(0, 6);

  const StockCard = ({ stock }: { stock: StockData }) => (
    <Link to={`/stocks/${stock.symbol}`} className="block group">
      <div className="p-4 rounded-xl border bg-white hover:shadow-md transition-all duration-200 transform hover:-translate-y-1">
        <div className="flex items-center justify-between mb-2">
          <div className="font-bold text-gray-900">{stock.symbol}</div>
          <div className={`flex items-center text-xs font-medium px-2 py-1 rounded-full ${stock.change_percent >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
            {stock.change_percent >= 0 ? <ArrowTrendingUpIcon className="w-3 h-3 mr-1" /> : <ArrowTrendingDownIcon className="w-3 h-3 mr-1" />}
            {Math.abs(stock.change_percent).toFixed(2)}%
          </div>
        </div>
        <div className="text-sm text-gray-500 truncate mb-3">{stock.name}</div>
        <div className="flex items-baseline justify-between">
          <div className="text-lg font-bold text-gray-900">{stock.formatted_price}</div>
          <div className="text-xs text-gray-400">{stock.sector}</div>
        </div>
      </div>
    </Link>
  );

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Hero Section */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto pt-20 pb-16 px-4 text-center">
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-gray-900 mb-6">
            stoxly<span className="text-green-600">.ai</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Real-time analysis and AI-powered insights for the Indian stock market.
          </p>

          <form onSubmit={onSearch} className="max-w-xl mx-auto relative">
            <div className="flex shadow-lg rounded-lg overflow-hidden">
              <input
                id="home-stock-search"
                name="stock_search"
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for a company (e.g., RELIANCE, TCS)"
                className="flex-1 px-6 py-4 border-none focus:ring-0 text-lg"
              />
              <button type="submit" className="px-8 py-4 bg-green-600 text-white font-semibold hover:bg-green-700 transition-colors">
                Search
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 space-y-12">
        {/* Top Gainers Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <span className="w-2 h-8 bg-green-500 rounded-full mr-3"></span>
              Market Movers
            </h2>
            <div className="flex items-center text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
              <span className="relative flex h-2 w-2 mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              Live Updates
            </div>
          </div>
          {isLoading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map(i => <div key={i} className="h-32 bg-gray-200 rounded-xl animate-pulse"></div>)}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
              {topGainers.map(stock => <StockCard key={stock.symbol} stock={stock} />)}
            </div>
          )}
        </section>

        {/* Penny Stocks Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <span className="w-2 h-8 bg-purple-500 rounded-full mr-3"></span>
              Penny Stocks
              <span className="ml-3 text-sm font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded">Under ₹50</span>
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {pennyStocks.map(stock => <StockCard key={stock.symbol} stock={stock} />)}
          </div>
          {pennyStocksAll.length > pennyLimit && (
            <div className="mt-6 text-center">
              <button
                onClick={() => setPennyLimit(prev => prev + 12)}
                className="px-6 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
              >
                Show More Penny Stocks ({pennyStocksAll.length - pennyLimit} remaining)
              </button>
            </div>
          )}
        </section>

        {/* Medium Range Stocks Section */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <span className="w-2 h-8 bg-blue-500 rounded-full mr-3"></span>
              Mid-Cap & Growth
              <span className="ml-3 text-sm font-normal text-gray-500 bg-gray-100 px-2 py-1 rounded">₹50 - ₹1000</span>
            </h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
            {mediumStocks.map(stock => <StockCard key={stock.symbol} stock={stock} />)}
          </div>
          {mediumStocksAll.length > mediumLimit && (
            <div className="mt-6 text-center">
              <button
                onClick={() => setMediumLimit(prev => prev + 12)}
                className="px-6 py-2 bg-white border border-gray-300 rounded-full text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
              >
                Show More Mid-Cap Stocks ({mediumStocksAll.length - mediumLimit} remaining)
              </button>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default Home;