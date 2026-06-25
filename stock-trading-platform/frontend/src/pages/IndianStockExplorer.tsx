import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  useGetAllIndianStocksQuery,
  useSearchIndianStocksQuery,
  useGetIndianStockPriceQuery,
  useGetStockHistoryQuery
} from '../services/api';
import { MagnifyingGlassIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface StockData {
  symbol: string;
  name: string;
  sector: string;
  market_cap_category: string;
  current_price: number;
  formatted_price: string;
  change: number;
  change_percent: number;
  is_nifty50: boolean;
  is_nifty100: boolean;
  volume: number;
  market_cap: number;
}

const IndianStockExplorer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const [selectedSector, setSelectedSector] = useState('');
  const [selectedMarketCap, setSelectedMarketCap] = useState('');
  const [selectedIndex, setSelectedIndex] = useState('');
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [chartPeriod, setChartPeriod] = useState('3m');
  const [chartInterval, setChartInterval] = useState('1d');

  // Fetch all Indian stocks with auto-refresh every 30 seconds
  const { data: allStocksData, isLoading, error, refetch } = useGetAllIndianStocksQuery(
    undefined,
    { pollingInterval: 30000 } // 30 seconds
  );
  
  // Manual refresh functionality
  const [lastRefresh, setLastRefresh] = useState(new Date());
  
  const handleRefresh = () => {
    refetch();
    setLastRefresh(new Date());
  };
  
  // Search stocks when query is not empty
  const { data: searchData } = useSearchIndianStocksQuery(
    { query: searchQuery, limit: 50 },
    { skip: searchQuery.length < 2 }
  );

  // Get detailed price for selected stock
  const { data: stockPrice } = useGetIndianStockPriceQuery(
    selectedStock || '',
    { skip: !selectedStock }
  );
  
  // Get stock history for chart
  const { data: stockHistory, isLoading: isLoadingHistory } = useGetStockHistoryQuery(
    { symbol: selectedStock || '', period: chartPeriod, interval: chartInterval },
    { skip: !selectedStock }
  );

  const stocks = useMemo(() => {
    if (searchQuery.length >= 2 && searchData) {
      return searchData.stocks.map(stock => ({
        ...stock,
        current_price: 0,
        formatted_price: '₹0.00',
        change: 0,
        change_percent: 0,
        volume: 0,
        market_cap: 0
      }));
    }
    return allStocksData?.stocks || [];
  }, [searchQuery, searchData, allStocksData]);

  const filteredStocks = useMemo(() => {
    return stocks.filter(stock => {
      const sectorMatch = !selectedSector || stock.sector === selectedSector;
      const marketCapMatch = !selectedMarketCap || stock.market_cap_category === selectedMarketCap;
      const indexMatch = !selectedIndex || 
        (selectedIndex === 'nifty50' && stock.is_nifty50) ||
        (selectedIndex === 'nifty100' && stock.is_nifty100);
      
      return sectorMatch && marketCapMatch && indexMatch;
    });
  }, [stocks, selectedSector, selectedMarketCap, selectedIndex]);

  const sectors = useMemo(() => {
    const uniqueSectors = Array.from(new Set(stocks.map(stock => stock.sector)));
    return uniqueSectors.sort();
  }, [stocks]);

  const handleStockSelect = (symbol: string) => {
    navigate(`/stocks/${symbol}`);
  };

  const StockCard: React.FC<{ stock: StockData }> = ({ stock }) => (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-lg shadow-md p-4 border border-gray-200 cursor-pointer hover:shadow-lg transition-shadow"
      onClick={() => handleStockSelect(stock.symbol)}
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-semibold text-gray-900">{stock.symbol}</h3>
          <p className="text-sm text-gray-600 line-clamp-2">{stock.name}</p>
        </div>
        <div className="text-right">
          <p className={`font-bold text-lg ${
            stock.current_price > 0 ? (
              stock.change >= 0 ? 'text-green-600' : 'text-red-600'
            ) : 'text-gray-500'
          }`}>
            {stock.formatted_price}
          </p>
          {stock.current_price > 0 && (
            <div className={`text-xs flex items-center justify-end ${
              stock.change >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {stock.change >= 0 ? (
                <ArrowTrendingUpIcon className="w-3 h-3 mr-1" />
              ) : (
                <ArrowTrendingDownIcon className="w-3 h-3 mr-1" />
              )}
              <span>
                ₹{Math.abs(stock.change).toFixed(2)} ({stock.change_percent.toFixed(2)}%)
              </span>
            </div>
          )}
          <div className="flex items-center justify-end space-x-1 mt-1">
            {stock.is_nifty50 && (
              <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                NIFTY 50
              </span>
            )}
            {stock.is_nifty100 && !stock.is_nifty50 && (
              <span className="inline-block bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                NIFTY 100
              </span>
            )}
          </div>
        </div>
      </div>
      
      <div className="flex justify-between items-center text-sm">
        <span className="text-gray-500">{stock.sector}</span>
        <span className={`px-2 py-1 rounded text-xs font-medium ${
          stock.market_cap_category === 'large' ? 'bg-blue-100 text-blue-800' :
          stock.market_cap_category === 'mid' ? 'bg-yellow-100 text-yellow-800' :
          'bg-purple-100 text-purple-800'
        }`}>
          {stock.market_cap_category.toUpperCase()}-CAP
        </span>
      </div>
    </motion.div>
  );

  const StockDetailModal: React.FC = () => {
    if (!selectedStock || !stockPrice) return null;

    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={() => setSelectedStock(null)}
      >
        <motion.div
          initial={{ scale: 0.9 }}
          animate={{ scale: 1 }}
          className="bg-white rounded-xl max-w-4xl w-full max-h-screen overflow-y-auto p-6"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{stockPrice.company_name}</h2>
              <p className="text-lg text-gray-600">{stockPrice.symbol}</p>
            </div>
            <button
              onClick={() => setSelectedStock(null)}
              className="text-gray-400 hover:text-gray-600 text-xl"
            >
              ×
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-3xl font-bold text-gray-900">{stockPrice.formatted_price}</p>
                  <div className="flex items-center mt-1">
                    {stockPrice.change >= 0 ? (
                      <ArrowTrendingUpIcon className="w-5 h-5 text-green-500 mr-1" />
                    ) : (
                      <ArrowTrendingDownIcon className="w-5 h-5 text-red-500 mr-1" />
                    )}
                    <span className={`font-medium ${stockPrice.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      ₹{Math.abs(stockPrice.change).toFixed(2)} ({stockPrice.change_percent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Previous Close</p>
                <p className="text-lg font-semibold">₹{stockPrice.previous_close.toFixed(2)}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Volume</p>
                <p className="text-lg font-semibold">{stockPrice.volume.toLocaleString()}</p>
              </div>
              {stockPrice.pe_ratio && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">P/E Ratio</p>
                  <p className="text-lg font-semibold">{stockPrice.pe_ratio.toFixed(2)}</p>
                </div>
              )}
              {stockPrice.dividend_yield && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">Dividend Yield</p>
                  <p className="text-lg font-semibold">{(stockPrice.dividend_yield * 100).toFixed(2)}%</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white border rounded-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Price Chart</h3>
              <div className="flex space-x-2">
                {[
                  { period: '5d', interval: '1h', label: '5D' },
                  { period: '1m', interval: '1d', label: '1M' },
                  { period: '3m', interval: '1d', label: '3M' },
                  { period: '6m', interval: '1d', label: '6M' },
                  { period: '1y', interval: '1d', label: '1Y' },
                  { period: '2y', interval: '1wk', label: '2Y' }
                ].map(({ period, interval, label }) => (
                  <button
                    key={period}
                    onClick={() => {
                      setChartPeriod(period);
                      setChartInterval(interval);
                    }}
                    className={`px-3 py-1 text-xs rounded-md transition-colors ${
                      chartPeriod === period
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="h-64">
              {isLoadingHistory ? (
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : stockHistory && stockHistory.data && stockHistory.data.length > 0 ? (
                <Line
                  data={{
                    labels: stockHistory.data.map(item => {
                      const date = new Date(item.date);
                      if (chartPeriod === '5d') {
                        return date.toLocaleDateString('en-IN', { 
                          month: 'short', 
                          day: 'numeric',
                          hour: '2-digit'
                        });
                      } else if (chartPeriod === '1y' || chartPeriod === '2y') {
                        return date.toLocaleDateString('en-IN', { 
                          year: '2-digit',
                          month: 'short'
                        });
                      } else {
                        return date.toLocaleDateString('en-IN', { 
                          month: 'short', 
                          day: 'numeric' 
                        });
                      }
                    }),
                    datasets: [
                      {
                        label: 'Price (₹)',
                        data: stockHistory.data.map(item => item.close),
                        borderColor: 'rgb(59, 130, 246)',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 1,
                        pointHoverRadius: 4,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                      tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                          label: function(context) {
                            return `Price: ₹${context.parsed.y.toFixed(2)}`;
                          }
                        }
                      },
                    },
                    interaction: {
                      mode: 'nearest',
                      axis: 'x',
                      intersect: false,
                    },
                    scales: {
                      x: {
                        display: true,
                        title: {
                          display: true,
                          text: 'Date'
                        },
                        grid: {
                          display: false
                        }
                      },
                      y: {
                        display: true,
                        title: {
                          display: true,
                          text: 'Price (₹)'
                        },
                        grid: {
                          color: 'rgba(0, 0, 0, 0.1)'
                        },
                        ticks: {
                          callback: function(value) {
                            return '₹' + value;
                          }
                        }
                      },
                    },
                  }}
                />
              ) : (
                <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">
                    {stockHistory ? 'No chart data available' : 'Loading chart data...'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </motion.div>
    );
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error loading Indian stocks. Please try again later.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Indian Stock Explorer</h1>
            <p className="text-gray-600">
              Discover and analyze Indian NSE stocks with real-time prices in ₹
            </p>
          </div>
          <div className="flex flex-col items-end">
            <button
              onClick={handleRefresh}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              disabled={isLoading}
            >
              <ArrowPathIcon className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            <p className="text-xs text-gray-500 mt-1">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </p>
            <p className="text-xs text-gray-400">
              Auto-refreshes every 30s
            </p>
          </div>
        </div>
      </motion.div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="bg-white rounded-lg shadow-md p-6 mb-8"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              id="indian-stocks-search"
              name="stock_search"
              type="search"
              placeholder="Search stocks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            id="indian-stocks-sector"
            name="sector"
            value={selectedSector}
            onChange={(e) => setSelectedSector(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Sectors</option>
            {sectors.map(sector => (
              <option key={sector} value={sector}>{sector}</option>
            ))}
          </select>

          <select
            id="indian-stocks-market-cap"
            name="market_cap"
            value={selectedMarketCap}
            onChange={(e) => setSelectedMarketCap(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Market Caps</option>
            <option value="large">Large Cap</option>
            <option value="mid">Mid Cap</option>
            <option value="small">Small Cap</option>
          </select>

          <select
            id="indian-stocks-index"
            name="index"
            value={selectedIndex}
            onChange={(e) => setSelectedIndex(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Stocks</option>
            <option value="nifty50">NIFTY 50</option>
            <option value="nifty100">NIFTY 100</option>
          </select>
        </div>

        <div className="text-sm text-gray-600">
          Showing {filteredStocks.length} stocks
          {searchQuery && ` for "${searchQuery}"`}
        </div>
      </motion.div>

      {/* Stock Grid */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
      >
        {filteredStocks.map((stock, index) => (
          <motion.div
            key={stock.symbol}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <StockCard stock={stock} />
          </motion.div>
        ))}
      </motion.div>

      {filteredStocks.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center py-12"
        >
          <p className="text-gray-500 text-lg">No stocks found matching your criteria</p>
        </motion.div>
      )}

      {/* Stock Detail Modal */}
      <StockDetailModal />
    </div>
  );
};

export default IndianStockExplorer;
