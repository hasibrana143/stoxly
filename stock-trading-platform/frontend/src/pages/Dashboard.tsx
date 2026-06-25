import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAppSelector } from '../hooks/redux';
import { useListPortfoliosQuery, useGetPortfolioDetailsQuery, useGetMarketMoversQuery, useGetWatchlistQuery } from '../services/api';
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const user = useAppSelector((state) => state.auth.user);
  const { data: watchlistData } = useGetWatchlistQuery();

  // Market Movers State
  const [moverType, setMoverType] = useState<'gainers' | 'losers'>('gainers');
  const { data: marketMoversData, isLoading: moversLoading, refetch: refetchMovers } = useGetMarketMoversQuery(
    { type: moverType, limit: 10 },
    { pollingInterval: 60000 } // Auto-refresh every 60 seconds
  );

  const { data: portfolios } = useListPortfoliosQuery();
  const { data: portfolioDetails } = useGetPortfolioDetailsQuery(
    portfolios?.portfolios[0]?.id || 0,
    { skip: !portfolios?.portfolios?.length }
  );

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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Portfolio Value</h3>
          <p className="text-2xl font-bold text-primary-600 mt-2">
            {portfolioDetails ? `₹${portfolioDetails.total_value.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '₹0.00'}
          </p>
          <p className={`text-sm mt-1 ${portfolioDetails && portfolioDetails.total_pnl >= 0 ? 'text-success-600' : 'text-red-600'}`}>
            {portfolioDetails ? (
              <>
                {portfolioDetails.total_pnl >= 0 ? '+' : ''}{portfolioDetails.total_pnl_percent.toFixed(2)}% All Time
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
          <p className="text-2xl font-bold text-gray-900 mt-2">{portfolioDetails?.holdings.length || 0}</p>
          <p className="text-sm text-gray-600 mt-1">Active positions</p>
        </Link>

        <Link to="/watchlist" className="card hover:shadow-md transition-shadow cursor-pointer group">
          <div className="flex justify-between items-start">
            <h3 className="text-lg font-semibold text-gray-900">Watchlist</h3>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400 group-hover:text-indigo-600 transition-colors" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
            </svg>
          </div>
          <p className="text-2xl font-bold text-gray-900 mt-2">{watchlistData?.watchlist?.length ?? 0}</p>
          <p className="text-sm text-gray-600 mt-1">Stocks tracking</p>
        </Link>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Total P&L</h3>
          <p className={`text-2xl font-bold mt-2 ${portfolioDetails && portfolioDetails.total_pnl >= 0 ? 'text-success-600' : 'text-red-600'}`}>
            {portfolioDetails ? (
              <>
                {portfolioDetails.total_pnl >= 0 ? '+' : ''}₹{Math.abs(portfolioDetails.total_pnl).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </>
            ) : '₹0.00'}
          </p>
          <p className={`text-sm mt-1 ${portfolioDetails && portfolioDetails.total_pnl >= 0 ? 'text-success-600' : 'text-red-600'}`}>
            {portfolioDetails ? `${portfolioDetails.total_pnl_percent.toFixed(2)}%` : '0.00%'}
          </p>
        </div>
      </div>

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
            <Link to="/portfolio" className="btn-secondary text-center">
              View Portfolio
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

export default Dashboard;
