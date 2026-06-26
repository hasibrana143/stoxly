import React from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
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
import {
  useGetScreenerStockDetailsQuery,
  useGetScreenerQuartersQuery,
  useGetScreenerPLQuery,
  useGetScreenerBalanceSheetQuery,
  useGetScreenerCashFlowQuery,
  useGetScreenerPeersQuery,
  useGetIndianStockPriceQuery,
  useGetStockHistoryQuery,
  useGetStockDetailsQuery,
  useGetWatchlistQuery,
  useAddToWatchlistMutation,
  useRemoveFromWatchlistMutation
} from '../services/api';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import {
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  InformationCircleIcon,
  ScaleIcon,
  DocumentTextIcon,
  TableCellsIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const StockDetails: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTab = searchParams.get('tab') || 'overview';

  // Watchlist hooks
  const { data: watchlistData } = useGetWatchlistQuery();
  const [addToWatchlist, { isLoading: isAdding }] = useAddToWatchlistMutation();
  const [removeFromWatchlist, { isLoading: isRemoving }] = useRemoveFromWatchlistMutation();

  // Queries
  // const { data: stockDetails, isLoading: isLoadingDetails, error: detailsError } = useGetStockDetailsQuery(symbol || '', { skip: !symbol });
  const { data: screenerDetails, isLoading: isLoadingScreener, error: screenerError } = useGetScreenerStockDetailsQuery(symbol || '', { skip: !symbol });
  const { data: quartersData } = useGetScreenerQuartersQuery(symbol || '', { skip: !symbol });
  const { data: plData } = useGetScreenerPLQuery(symbol || '', { skip: !symbol });
  const { data: balanceData } = useGetScreenerBalanceSheetQuery(symbol || '', { skip: !symbol });
  const { data: cashFlowData } = useGetScreenerCashFlowQuery(symbol || '', { skip: !symbol });
  const { data: peersData } = useGetScreenerPeersQuery(symbol || '', { skip: !symbol });
  const { data: livePrice, isLoading: isLoadingPrice } = useGetIndianStockPriceQuery(symbol || '', { pollingInterval: 5000, skip: !symbol });
  const { data: history } = useGetStockHistoryQuery({ symbol: symbol || '', period: '1y' }, { skip: !symbol });

  const watchlistItem = watchlistData?.watchlist?.find((item) => item.symbol === symbol);
  const isFollowing = !!watchlistItem;

  const toggleFollow = async () => {
    if (!symbol) return;
    try {
      if (isFollowing) {
        if (watchlistItem) {
          await removeFromWatchlist(watchlistItem.id).unwrap();
          toast.success('Removed from watchlist');
        }
      } else {
        await addToWatchlist({ symbol }).unwrap();
        toast.success('Added to watchlist');
      }
    } catch (error) {
      console.error('Failed to update watchlist:', error);
      toast.error('Failed to update watchlist');
    }
  };

  const setActiveTab = (tab: string) => {
    setSearchParams({ tab });
  };

  const formatCurrency = (value: number | undefined) => {
    if (value === undefined) return '-';
    if (value >= 100000) return `₹${(value / 100000).toFixed(1)}L Cr`;
    if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K Cr`;
    return `₹${value.toFixed(0)} Cr`;
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined) return '-';
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (isLoadingScreener || isLoadingPrice) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Only show error if both sources fail
  if ((screenerError && !livePrice) || (!screenerDetails && !livePrice)) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline"> Failed to load stock details. The stock might not exist or there was a network error.</span>
          </div>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Merge details with fallback
  const displayDetails = {
    name: screenerDetails?.name || livePrice?.company_name || symbol || 'Unknown Stock',
    sector: screenerDetails?.sector || 'N/A',
    industry: screenerDetails?.industry || 'N/A',
    market_cap_category: screenerDetails?.market_cap_category || 'N/A',
    website: screenerDetails?.website || '#',
    roe: screenerDetails?.roe,
    roce: screenerDetails?.roce,
    book_value: screenerDetails?.book_value,
    dividend_yield: screenerDetails?.dividend_yield || livePrice?.dividend_yield,
    market_cap: screenerDetails?.market_cap || livePrice?.market_cap || 0,
    pe_ratio: screenerDetails?.pe_ratio || livePrice?.pe_ratio || 0,
    price_change_1w: screenerDetails?.price_change_1w || 0,
    price_change_1m: screenerDetails?.price_change_1m || 0,
    price_change_3m: screenerDetails?.price_change_3m || 0,
    price_change_6m: screenerDetails?.price_change_6m || 0,
    price_change_1y: screenerDetails?.price_change_1y || 0,
    week_52_high: screenerDetails?.week_52_high || 0,
    week_52_low: screenerDetails?.week_52_low || 0,
    pros: screenerDetails?.pros || [],
    cons: screenerDetails?.cons || [],
  };

  // Use live price if available, otherwise fallback to details price
  const currentPrice = livePrice?.current_price || screenerDetails?.current_price || 0;
  const priceChange = livePrice?.change || 0;
  const priceChangePercent = livePrice?.change_percent || 0;

  const tabs = [
    { key: 'overview', label: 'Overview', icon: InformationCircleIcon },
    { key: 'chart', label: 'Chart', icon: ChartBarIcon },
    { key: 'analysis', label: 'Analysis', icon: DocumentTextIcon },
    { key: 'peers', label: 'Peers', icon: ScaleIcon },
    { key: 'quarters', label: 'Quarters', icon: TableCellsIcon },
    { key: 'profit_loss', label: 'Profit & Loss', icon: TableCellsIcon },
    { key: 'balance_sheet', label: 'Balance Sheet', icon: TableCellsIcon },
    { key: 'cash_flow', label: 'Cash Flows', icon: TableCellsIcon },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto space-y-6">

        {/* Header Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{displayDetails.name}</h1>
              <div className="flex items-center space-x-2 mt-1 text-sm text-gray-500">
                <span className="font-medium text-gray-700">{symbol}</span>
                <span>•</span>
                <span>{displayDetails.sector}</span>
                <span>•</span>
                <a href={displayDetails.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                  Website
                </a>
              </div>
            </div>
            <div className="mt-4 md:mt-0 text-right">
              <div className="text-3xl font-bold text-gray-900">
                ₹{currentPrice.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
              </div>
              <div className={`flex items-center justify-end space-x-1 ${priceChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {priceChange >= 0 ? <ArrowTrendingUpIcon className="h-4 w-4" /> : <ArrowTrendingDownIcon className="h-4 w-4" />}
                <span className="font-medium">{Math.abs(priceChange).toFixed(2)} ({Math.abs(priceChangePercent).toFixed(2)}%)</span>
              </div>
              <div className="text-xs text-gray-400 mt-1">Live Data</div>
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 pt-6 border-t border-gray-100">
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">Market Cap</div>
              <div className="font-semibold text-gray-900">{formatCurrency(displayDetails.market_cap)}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">Stock P/E</div>
              <div className="font-semibold text-gray-900">{displayDetails.pe_ratio?.toFixed(1) || '-'}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">ROCE</div>
              <div className="font-semibold text-gray-900">{displayDetails.roce?.toFixed(1)}%</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">ROE</div>
              <div className="font-semibold text-gray-900">{displayDetails.roe?.toFixed(1)}%</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">Book Value</div>
              <div className="font-semibold text-gray-900">₹{displayDetails.book_value?.toFixed(1)}</div>
            </div>
            <div>
              <div className="text-xs text-gray-500 uppercase tracking-wider">Div. Yield</div>
              <div className="font-semibold text-gray-900">{displayDetails.dividend_yield?.toFixed(2)}%</div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="border-b border-gray-200 px-6 py-3 flex justify-between items-center">
            <nav className="flex space-x-6 overflow-x-auto scrollbar-hide">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`flex items-center space-x-2 py-2 border-b-2 text-sm font-medium whitespace-nowrap ${activeTab === tab.key
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
            <button
              onClick={toggleFollow}
              className={`ml-4 px-4 py-1.5 text-sm font-medium rounded-lg transition-colors ${isFollowing
                ? 'bg-blue-50 text-blue-700 hover:bg-blue-100'
                : 'bg-gray-900 text-white hover:bg-gray-800'
                }`}
            >
              {isFollowing ? 'Following' : '+ Follow'}
            </button>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  <div className="lg:col-span-2 space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">About {displayDetails.name}</h3>
                      <p className="text-gray-600 leading-relaxed">
                        {displayDetails.name} is a leading player in the {displayDetails.sector} sector.
                        The company operates primarily in {displayDetails.industry}.
                        With a market capitalization of {formatCurrency(displayDetails.market_cap)}, it is classified as a {displayDetails.market_cap_category} Cap company.
                      </p>
                    </div>

                    {/* Price Chart Preview */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Price Chart (1Y)</h3>
                      <div className="h-64 w-full bg-gray-50 rounded-lg p-4 border border-gray-100">
                        {history ? (
                          <Line
                            data={{
                              labels: history.data.map((d: any) => d.date),
                              datasets: [{
                                label: 'Price',
                                data: history.data.map((d: any) => d.close),
                                borderColor: '#2563eb',
                                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                                fill: true,
                                tension: 0.4,
                                pointRadius: 0
                              }]
                            }}
                            options={{
                              responsive: true,
                              maintainAspectRatio: false,
                              plugins: { legend: { display: false } },
                              scales: { x: { display: false }, y: { display: true } }
                            }}
                          />
                        ) : (
                          <div className="h-full flex items-center justify-center text-gray-400">Loading chart...</div>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                      <h3 className="font-semibold text-gray-900 mb-3">Performance</h3>
                      <div className="space-y-3">
                        {[
                          { label: '1 Week', value: displayDetails.price_change_1w },
                          { label: '1 Month', value: displayDetails.price_change_1m },
                          { label: '3 Months', value: displayDetails.price_change_3m },
                          { label: '6 Months', value: displayDetails.price_change_6m },
                          { label: '1 Year', value: displayDetails.price_change_1y },
                        ].map((item) => (
                          <div key={item.label} className="flex justify-between items-center text-sm">
                            <span className="text-gray-600">{item.label}</span>
                            <span className={`font-medium ${item.value >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                              {formatPercentage(item.value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4 border border-gray-100">
                      <h3 className="font-semibold text-gray-900 mb-3">52 Week Range</h3>
                      <div className="space-y-4">
                        <div className="flex justify-between text-sm text-gray-600">
                          <span>Low: ₹{displayDetails.week_52_low}</span>
                          <span>High: ₹{displayDetails.week_52_high}</span>
                        </div>
                        <div className="relative h-2 bg-gray-200 rounded-full">
                          <div
                            className="absolute h-full bg-blue-600 rounded-full"
                            style={{
                              left: `${((currentPrice - displayDetails.week_52_low) / (displayDetails.week_52_high - displayDetails.week_52_low)) * 100}%`,
                              width: '8px',
                              transform: 'translateX(-50%)'
                            }}
                          />
                        </div>
                        <div className="text-center text-sm font-medium text-gray-900">
                          Current: ₹{currentPrice.toFixed(2)}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Chart Tab */}
            {activeTab === 'chart' && (
              <div className="h-[500px]">
                {history ? (
                  <Line
                    data={{
                      labels: history.data.map((d: any) => d.date),
                      datasets: [{
                        label: 'Stock Price',
                        data: history.data.map((d: any) => d.close),
                        borderColor: '#2563eb',
                        backgroundColor: 'rgba(37, 99, 235, 0.1)',
                        fill: true,
                        tension: 0.1,
                        pointRadius: 1,
                        pointHoverRadius: 4
                      }]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: { display: false },
                        tooltip: { mode: 'index', intersect: false }
                      },
                      scales: {
                        x: { grid: { display: false } },
                        y: { grid: { color: '#f3f4f6' } }
                      }
                    }}
                  />
                ) : (
                  <div className="h-full flex items-center justify-center text-gray-400">Loading chart data...</div>
                )}
              </div>
            )}

            {/* Analysis Tab */}
            {activeTab === 'analysis' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-green-50 rounded-lg p-6 border border-green-100">
                  <h3 className="text-lg font-semibold text-green-800 mb-4">Pros</h3>
                  <ul className="space-y-2">
                    {displayDetails.pros?.map((pro: string, i: number) => (
                      <li key={i} className="flex items-start text-green-700">
                        <span className="mr-2">•</span>
                        <span>{pro}</span>
                      </li>
                    )) || <li className="text-green-700">Company has good consistent profit growth.</li>}
                  </ul>
                </div>
                <div className="bg-red-50 rounded-lg p-6 border border-red-100">
                  <h3 className="text-lg font-semibold text-red-800 mb-4">Cons</h3>
                  <ul className="space-y-2">
                    {displayDetails.cons?.map((con: string, i: number) => (
                      <li key={i} className="flex items-start text-red-700">
                        <span className="mr-2">•</span>
                        <span>{con}</span>
                      </li>
                    )) || <li className="text-red-700">Stock is trading at high valuation.</li>}
                  </ul>
                </div>
              </div>
            )}

            {/* Peers Tab */}
            {activeTab === 'peers' && peersData && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">P/E</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Market Cap</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Div Yield</th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ROCE %</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {peersData.peers.map((peer: any) => (
                      <tr key={peer.symbol} className={peer.symbol === symbol ? 'bg-blue-50' : 'hover:bg-gray-50'}>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="font-medium text-gray-900">{peer.name}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          ₹{peer.current_price.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {peer.pe_ratio?.toFixed(2) || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {formatCurrency(peer.market_cap)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {peer.dividend_yield?.toFixed(2)}%
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                          {peer.roce?.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Quarters Tab */}
            {activeTab === 'quarters' && quartersData && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Particulars</th>
                      {quartersData.quarters.map((q: any) => (
                        <th key={q.period} className="px-4 py-3 text-right font-medium text-gray-500">{q.period}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Sales</td>
                      {quartersData.quarters.map((q: any) => (
                        <td key={q.period} className="px-4 py-3 text-right">{q.sales}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Expenses</td>
                      {quartersData.quarters.map((q: any) => (
                        <td key={q.period} className="px-4 py-3 text-right">{q.expenses}</td>
                      ))}
                    </tr>
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-gray-900">Operating Profit</td>
                      {quartersData.quarters.map((q: any) => (
                        <td key={q.period} className="px-4 py-3 text-right">{q.operating_profit}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">OPM %</td>
                      {quartersData.quarters.map((q: any) => (
                        <td key={q.period} className="px-4 py-3 text-right">{q.opm_percent}%</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Net Profit</td>
                      {quartersData.quarters.map((q: any) => (
                        <td key={q.period} className="px-4 py-3 text-right">{q.net_profit}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">EPS in Rs</td>
                      {quartersData.quarters.map((q: any) => (
                        <td key={q.period} className="px-4 py-3 text-right">{q.eps}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Profit & Loss Tab */}
            {activeTab === 'profit_loss' && plData && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Particulars</th>
                      {plData.profit_loss.map((y: any) => (
                        <th key={y.year} className="px-4 py-3 text-right font-medium text-gray-500">{y.year}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Sales</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.sales}</td>
                      ))}
                    </tr>
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-gray-900">Operating Profit</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.operating_profit}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Other Income</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.other_income}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Interest</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.interest}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Depreciation</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.depreciation}</td>
                      ))}
                    </tr>
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-gray-900">Net Profit</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.net_profit}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">EPS in Rs</td>
                      {plData.profit_loss.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.eps}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Balance Sheet Tab */}
            {activeTab === 'balance_sheet' && balanceData && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Particulars</th>
                      {balanceData.balance_sheet.map((y: any) => (
                        <th key={y.year} className="px-4 py-3 text-right font-medium text-gray-500">{y.year}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Share Capital</td>
                      {balanceData.balance_sheet.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.shareholders_equity}</td> // Simplified
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Borrowings</td>
                      {balanceData.balance_sheet.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.debt}</td>
                      ))}
                    </tr>
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-gray-900">Total Liabilities</td>
                      {balanceData.balance_sheet.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.total_liabilities}</td>
                      ))}
                    </tr>
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-gray-900">Total Assets</td>
                      {balanceData.balance_sheet.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.total_assets}</td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {/* Cash Flow Tab */}
            {activeTab === 'cash_flow' && cashFlowData && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium text-gray-500">Particulars</th>
                      {cashFlowData.cash_flow.map((y: any) => (
                        <th key={y.year} className="px-4 py-3 text-right font-medium text-gray-500">{y.year}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Cash from Operating Activity</td>
                      {cashFlowData.cash_flow.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.operating_cash_flow}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Cash from Investing Activity</td>
                      {cashFlowData.cash_flow.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.investing_cash_flow}</td>
                      ))}
                    </tr>
                    <tr>
                      <td className="px-4 py-3 font-medium text-gray-900">Cash from Financing Activity</td>
                      {cashFlowData.cash_flow.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">{y.financing_cash_flow}</td>
                      ))}
                    </tr>
                    <tr className="bg-gray-50 font-semibold">
                      <td className="px-4 py-3 text-gray-900">Net Cash Flow</td>
                      {cashFlowData.cash_flow.map((y: any) => (
                        <td key={y.year} className="px-4 py-3 text-right">
                          {y.operating_cash_flow + y.investing_cash_flow + y.financing_cash_flow}
                        </td>
                      ))}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockDetails;