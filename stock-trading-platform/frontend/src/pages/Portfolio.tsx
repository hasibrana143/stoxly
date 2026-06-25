import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  useListPortfoliosQuery,
  useCreatePortfolioMutation,
  useGetPortfolioDetailsQuery,
  useAddPortfolioItemMutation,
  useDeletePortfolioItemMutation,
  useSearchIndianStocksQuery,
  useGetAllIndianStocksQuery,
  useGetMarketMoversQuery,
  useGetWatchlistQuery
} from '../services/api';
import toast from 'react-hot-toast';
import { PlusIcon, TrashIcon, ArrowLeftIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { useAppSelector } from '../hooks/redux';

const Portfolio: React.FC = () => {
  const user = useAppSelector((state) => state.auth.user);
  const { data: portfolios } = useListPortfoliosQuery();
  const [createPortfolio] = useCreatePortfolioMutation();
  const [addPortfolioItem] = useAddPortfolioItemMutation();
  const [deletePortfolioItem] = useDeletePortfolioItemMutation();

  const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
  // const [showCreateForm, setShowCreateForm] = useState(false); // unused
  const [showAddStockForm, setShowAddStockForm] = useState(false);

  const [newPortfolio, setNewPortfolio] = useState({ name: '', description: '' });
  const [stockSearchQuery, setStockSearchQuery] = useState('');
  const [selectedStock, setSelectedStock] = useState<any>(null);
  const [newItem, setNewItem] = useState({ quantity: 1, average_price: 0 });

  const { data: portfolioDetails, isLoading: isLoadingDetails } = useGetPortfolioDetailsQuery(
    selectedPortfolioId || 0,
    { skip: !selectedPortfolioId, pollingInterval: 30000 }
  );

  // Load first portfolio for summary cards
  const { data: firstPortfolioDetails } = useGetPortfolioDetailsQuery(
    portfolios?.portfolios[0]?.id || 0,
    { skip: !portfolios?.portfolios?.length || !!selectedPortfolioId, pollingInterval: 30000 }
  );

  const { data: searchResults } = useSearchIndianStocksQuery(
    { query: stockSearchQuery },
    { skip: stockSearchQuery.length < 2 }
  );

  const [stocksData, isLoadingStocks] = [null, false]; // ESLint fix - unused but defined

  const { data: watchlistData } = useGetWatchlistQuery();
  const watchlistCount = watchlistData?.watchlist?.length || 0;

  // Market Movers State
  const [moverType, setMoverType] = useState<'gainers' | 'losers'>('gainers');
  const { data: marketMoversData, isLoading: moversLoading, refetch: refetchMovers } = useGetMarketMoversQuery(
    { type: moverType, limit: 10 },
    { pollingInterval: 60000 } // Auto-refresh every 60 seconds
  );



  const handleAddStock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPortfolioId || !selectedStock) return;

    try {
      await addPortfolioItem({
        portfolioId: selectedPortfolioId,
        symbol: selectedStock.symbol,
        quantity: Number(newItem.quantity),
        average_price: Number(newItem.average_price)
      }).unwrap();

      setShowAddStockForm(false);
      setStockSearchQuery('');
      setSelectedStock(null);
      setNewItem({ quantity: 1, average_price: 0 });
      toast.success('Stock added to portfolio!');
    } catch (error) {
      toast.error('Failed to add stock');
    }
  };

  const handleDeleteItem = async (itemId: number) => {
    if (!selectedPortfolioId) return;
    if (!window.confirm('Are you sure you want to remove this stock?')) return;

    try {
      await deletePortfolioItem({
        portfolioId: selectedPortfolioId,
        itemId
      }).unwrap();
      toast.success('Stock removed from portfolio');
    } catch (error) {
      toast.error('Failed to remove stock');
    }
  };

  // If viewing a specific portfolio, show detailed view
  if (selectedPortfolioId) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <button
          onClick={() => setSelectedPortfolioId(null)}
          className="flex items-center text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeftIcon className="h-5 w-5 mr-2" />
          Back to Portfolio
        </button>

        {isLoadingDetails ? (
          <div className="text-center py-12">Loading portfolio details...</div>
        ) : portfolioDetails ? (
          <>
            <div className="flex justify-between items-start mb-8">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{portfolioDetails.name}</h1>
                <p className="text-gray-600 mt-1">{portfolioDetails.description}</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-500">Total Value</div>
                <div className="text-3xl font-bold text-gray-900">
                  ₹{portfolioDetails.total_value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
                <div className={`text-sm font-medium ${portfolioDetails.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {portfolioDetails.total_pnl >= 0 ? '+' : ''}
                  ₹{Math.abs(portfolioDetails.total_pnl).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  {' '}({portfolioDetails.total_pnl_percent.toFixed(2)}%)
                </div>
              </div>
            </div>

            <div className="card mb-8">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Holdings</h2>
                <button
                  onClick={() => setShowAddStockForm(true)}
                  className="btn-primary flex items-center"
                >
                  <PlusIcon className="h-5 w-5 mr-2" />
                  Add Stock
                </button>
              </div>

              {showAddStockForm && (
                <div className="bg-gray-50 p-4 rounded-lg mb-6 border">
                  <h3 className="font-medium mb-4">Add Stock to Portfolio</h3>
                  <form onSubmit={handleAddStock} className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Search Stock</label>
                      <div className="relative">
                        <input
                          id="portfolio-stock-search"
                          name="stock_search"
                          type="search"
                          className="input-field"
                          placeholder="Type symbol or name (e.g., TCS, Reliance)"
                          value={stockSearchQuery}
                          onChange={(e) => {
                            setStockSearchQuery(e.target.value);
                            if (!e.target.value) setSelectedStock(null);
                          }}
                        />
                        {stockSearchQuery.length >= 2 && searchResults?.stocks && !selectedStock && (
                          <div className="absolute z-10 w-full bg-white mt-1 border rounded-md shadow-lg max-h-60 overflow-auto">
                            {searchResults.stocks.map((stock) => (
                              <div
                                key={stock.symbol}
                                className="p-2 hover:bg-gray-100 cursor-pointer"
                                onClick={() => {
                                  setSelectedStock(stock);
                                  setStockSearchQuery(`${stock.symbol} - ${stock.name}`);
                                }}
                              >
                                <div className="font-medium">{stock.symbol}</div>
                                <div className="text-xs text-gray-500">{stock.name}</div>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {selectedStock && (
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label htmlFor="portfolio-holding-quantity" className="block text-sm font-medium text-gray-700 mb-1">Quantity</label>
                          <input
                            id="portfolio-holding-quantity"
                            name="quantity"
                            type="number"
                            min="1"
                            step="1"
                            className="input-field"
                            value={newItem.quantity}
                            onChange={(e) => setNewItem({ ...newItem, quantity: Number(e.target.value) })}
                            required
                          />
                        </div>
                        <div>
                          <label htmlFor="portfolio-holding-average-price" className="block text-sm font-medium text-gray-700 mb-1">Average Buy Price (₹)</label>
                          <input
                            id="portfolio-holding-average-price"
                            name="average_price"
                            type="number"
                            min="0"
                            step="0.01"
                            className="input-field"
                            value={newItem.average_price}
                            onChange={(e) => setNewItem({ ...newItem, average_price: Number(e.target.value) })}
                            required
                          />
                        </div>
                      </div>
                    )}

                    <div className="flex gap-3">
                      <button
                        type="submit"
                        className="btn-primary"
                        disabled={!selectedStock}
                      >
                        Add to Portfolio
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setShowAddStockForm(false);
                          setStockSearchQuery('');
                          setSelectedStock(null);
                        }}
                        className="btn-secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              )}

              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Avg. Price</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">LTP</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Current Value</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {portfolioDetails.holdings.map((holding) => (
                      <tr key={holding.id}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-gray-900">{holding.symbol}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {holding.quantity}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ₹{holding.average_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ₹{holding.current_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                          ₹{holding.current_value.toFixed(2)}
                        </td>
                        <td className={`px-6 py-4 whitespace-nowrap text-right text-sm font-medium ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {holding.pnl >= 0 ? '+' : ''}₹{Math.abs(holding.pnl).toFixed(2)}
                          <div className="text-xs">
                            ({holding.pnl_percent.toFixed(2)}%)
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            onClick={() => handleDeleteItem(holding.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <TrashIcon className="h-5 w-5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                    {portfolioDetails.holdings.length === 0 && (
                      <tr>
                        <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                          No stocks in this portfolio yet. Click "Add Stock" to get started.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12 text-red-600">Portfolio not found</div>
        )}
      </div>
    );
  }

  // Main portfolio dashboard view
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.username || 'Trader'}!
        </h1>
        <p className="mt-2 text-gray-600">
          Here's your trading dashboard overview
        </p>
      </div>

      {/* Portfolio Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Portfolio Value</h3>
          <p className="text-2xl font-bold text-primary-600 mt-2">
            {firstPortfolioDetails ? `₹${firstPortfolioDetails.total_value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '₹0.00'}
          </p>
          <p className={`text-sm mt-1 ${firstPortfolioDetails && firstPortfolioDetails.total_pnl >= 0 ? 'text-success-600' : 'text-red-600'}`}>
            {firstPortfolioDetails ? (
              <>
                {firstPortfolioDetails.total_pnl >= 0 ? '+' : ''}{firstPortfolioDetails.total_pnl_percent.toFixed(2)}% All Time
              </>
            ) : 'Start investing'}
          </p>
        </div>

        <Link to="/portfolio/holdings" className="card hover:shadow-md transition-shadow cursor-pointer group">
          <div className="flex justify-between items-start">
            <h3 className="text-lg font-semibold text-gray-900">Total Stocks</h3>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{firstPortfolioDetails?.holdings.length || 0}</p>
          <p className="text-sm text-gray-600 mt-1">Active positions</p>
        </Link>

        <Link to="/watchlist" className="card hover:shadow-md transition-shadow cursor-pointer group">
          <div className="flex justify-between items-start">
            <h3 className="text-lg font-semibold text-gray-900">Watchlist</h3>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{watchlistCount}</p>
          <p className="text-sm text-gray-600 mt-1">Stocks tracking</p>
        </Link>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Total P&L</h3>
          <p className={`text-2xl font-bold mt-2 ${firstPortfolioDetails && firstPortfolioDetails.total_pnl >= 0 ? 'text-success-600' : 'text-red-600'}`}>
            {firstPortfolioDetails ? (
              <>
                {firstPortfolioDetails.total_pnl >= 0 ? '+' : ''}₹{Math.abs(firstPortfolioDetails.total_pnl).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </>
            ) : '₹0.00'}
          </p>
          <p className={`text-sm mt-1 ${firstPortfolioDetails && firstPortfolioDetails.total_pnl >= 0 ? 'text-success-600' : 'text-red-600'}`}>
            {firstPortfolioDetails ? `${firstPortfolioDetails.total_pnl_percent.toFixed(2)}%` : '0.00%'}
          </p>
        </div>
      </div>

      {/* Quick Actions and Market Movers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-4">
            <Link to="/stocks" className="btn-primary text-center">
              Search Stocks
            </Link>
            <Link to="/optimizer" className="btn-secondary text-center">
              Optimize Portfolio
            </Link>
            <Link to="/chat" className="btn-primary text-center">
              AI Assistant
            </Link>
            <Link to="/portfolio/manage" className="btn-secondary text-center">
              Manage Portfolio
            </Link>
          </div>
        </div>

        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Market Movers</h2>
            <div className="flex items-center space-x-2">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setMoverType('gainers')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${moverType === 'gainers' ? 'bg-white text-green-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                  Top Gainers
                </button>
                <button
                  onClick={() => setMoverType('losers')}
                  className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${moverType === 'losers' ? 'bg-white text-red-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'
                    }`}
                >
                  Top Losers
                </button>
              </div>
              <button
                onClick={() => refetchMovers()}
                className="p-1 text-gray-400 hover:text-indigo-600 transition-colors"
                title="Refresh"
              >
                <ArrowPathIcon className={`h-5 w-5 ${moversLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>
          </div>

          <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
            {moversLoading && !marketMoversData ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
              </div>
            ) : marketMoversData?.stocks && marketMoversData.stocks.length > 0 ? (
              marketMoversData.stocks.map((stock) => (
                <Link to={`/stocks/${stock.symbol}`} key={stock.symbol} className="flex justify-between items-center py-2 border-b border-gray-50 hover:bg-gray-50 transition-colors rounded-lg px-2">
                  <div className="flex items-center">
                    <span className="text-gray-400 font-medium text-xs w-6">#{stock.rank}</span>
                    <div>
                      <span className="font-medium text-sm text-indigo-600">{stock.symbol.replace('.NS', '')}</span>
                      <div className="text-xs text-gray-500 truncate max-w-[120px]">{stock.name}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold text-sm">₹{stock.current_price.toFixed(2)}</div>
                    <div className={`text-xs flex items-center justify-end ${stock.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {stock.change_percent >= 0 ? (
                        <ArrowTrendingUpIcon className="w-3 h-3 mr-1" />
                      ) : (
                        <ArrowTrendingDownIcon className="w-3 h-3 mr-1" />
                      )}
                      {Math.abs(stock.change_percent).toFixed(2)}%
                    </div>
                  </div>
                </Link>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                No market data available
              </div>
            )}
          </div>
          <div className="mt-3 flex justify-between items-center text-xs text-gray-400">
            <div className="flex items-center">
              <span className="relative flex h-2 w-2 mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
              </span>
              Live Updates
            </div>
            <span>Auto-refreshing every 60s</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Portfolio;
