import React, { useState, useEffect } from 'react';
import { FunnelIcon } from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';
import { useAppSelector } from '../hooks/redux';

interface Stock {
  symbol: string;
  name: string;
  sector: string;
  current_price: number;
  market_cap: number;
  market_cap_category: string;
  pe_ratio: number | null;
  pb_ratio: number;
  roe: number;
  debt_to_equity: number;
  dividend_yield: number;
  revenue_growth_1y: number;
  profit_growth_1y: number;
  price_change_1y: number;
  screener_score: number;
}

interface ScreenerFilters {
  market_cap_min?: number;
  market_cap_max?: number;
  market_cap_category?: string[];
  pe_ratio_min?: number;
  pe_ratio_max?: number;
  pb_ratio_min?: number;
  pb_ratio_max?: number;
  roe_min?: number;
  roe_max?: number;
  revenue_growth_1y_min?: number;
  profit_growth_1y_min?: number;
  debt_to_equity_max?: number;
  dividend_yield_min?: number;
  sectors?: string[];
  only_nifty50?: boolean;
  only_nifty100?: boolean;
  sort_by?: string;
  sort_order?: string;
  page?: number;
  limit?: number;
}

const Screener: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<ScreenerFilters>({
    sort_by: 'market_cap',
    sort_order: 'desc',
    page: 1,
    limit: 50
  });
  const [showFilters, setShowFilters] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [savedFilters, setSavedFilters] = useState<any[]>([]);
  const [filterName, setFilterName] = useState('');
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const token = useAppSelector((s) => s.auth.token);

  const marketCapCategories = ['large', 'mid', 'small'];

  const sortOptions = [
    { value: 'market_cap', label: 'Market Cap' },
    { value: 'pe_ratio', label: 'P/E Ratio' },
    { value: 'pb_ratio', label: 'P/B Ratio' },
    { value: 'roe', label: 'ROE' },
    { value: 'revenue_growth_1y', label: 'Revenue Growth' },
    { value: 'profit_growth_1y', label: 'Profit Growth' },
    { value: 'dividend_yield', label: 'Dividend Yield' },
    { value: 'screener_score', label: 'Screener Score' }
  ];

  const presets = {
    value_stocks: { name: 'Value Stocks', filters: { pe_ratio_max: 15, pb_ratio_max: 2, roe_min: 15 } },
    growth_stocks: { name: 'Growth Stocks', filters: { revenue_growth_1y_min: 15, profit_growth_1y_min: 20 } },
    dividend_stocks: { name: 'Dividend Stocks', filters: { dividend_yield_min: 3 } },
    nifty50: { name: 'Nifty 50', filters: { only_nifty50: true } }
  };

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      try {
        const response = await fetch('http://localhost:8000/api/screener/screen', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(filters)
        });
        if (response.ok) {
          const data = await response.json();
          setStocks(data.stocks);
          setTotalCount(data.total_count);
          setCurrentPage(data.page);
          setTotalPages(data.total_pages);
        }
      } catch (error) {
        console.error('Error screening stocks:', error);
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [filters]);

  useEffect(() => {
    const loadSaved = async () => {
      try {
        const resp = await fetch('http://localhost:8000/api/screener/filters/list', {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (resp.ok) {
          const data = await resp.json();
          setSavedFilters(data.filters || []);
        }
      } catch (e) { }
    };
    loadSaved();
  }, [token]);

  const handleFilterChange = (key: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
      page: 1 // Reset to first page when filters change
    }));
    // If manually changing filters, we might want to clear the active preset visual
    // setActiveFilter(null); // Optional: decide if manual changes should clear preset highlight
  };

  const handlePresetFilter = (presetKey: string) => {
    if (activeFilter === presetKey) {
      // Toggle OFF: Clear filters and reset active state
      clearFilters();
      setActiveFilter(null);
    } else {
      // Toggle ON: Apply preset filters
      const preset = presets[presetKey as keyof typeof presets];

      // Reset to base state first, then apply preset
      const baseFilters = {
        sort_by: 'market_cap',
        sort_order: 'desc',
        page: 1,
        limit: 50
      };

      setFilters({
        ...baseFilters,
        ...preset.filters
      });
      setActiveFilter(presetKey);
    }
  };

  const clearFilters = () => {
    setFilters({
      sort_by: 'market_cap',
      sort_order: 'desc',
      page: 1,
      limit: 50
    });
    setActiveFilter(null);
  };

  const formatCurrency = (value: number) => {
    if (value >= 10000) {
      return `₹${(value / 10000).toFixed(1)}L Cr`;
    } else if (value >= 100) {
      return `₹${(value / 100).toFixed(0)}K Cr`;
    }
    return `₹${value.toFixed(0)} Cr`;
  };

  const formatPercentage = (value: number) => {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const getChangeColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Stock Screener</h1>
          <p className="text-gray-600">Screen companies by key ratios and trends</p>
        </div>

        {/* Filter Controls */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                <FunnelIcon className="h-5 w-5" />
                <span>Filters</span>
              </button>

              <div className="flex space-x-2">
                {Object.entries(presets).map(([key, preset]) => (
                  <button
                    key={key}
                    onClick={() => handlePresetFilter(key)}
                    className={`px-3 py-1 text-sm rounded-md transition-colors ${activeFilter === key
                      ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-sm'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                  >
                    {preset.name}
                  </button>
                ))}
                {savedFilters.map((sf: any) => (
                  <button
                    key={sf.id}
                    onClick={() => {
                      try {
                        const crit = JSON.parse(sf.filter_criteria);
                        setFilters({ ...filters, ...crit, page: 1 });
                      } catch { }
                    }}
                    className="px-3 py-1 text-sm bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100"
                    title={sf.filter_name}
                  >
                    {sf.filter_name}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <select
                id="screener-sort-by"
                name="sort_by"
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>

              <select
                id="screener-sort-order"
                name="sort_order"
                value={filters.sort_order}
                onChange={(e) => handleFilterChange('sort_order', e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="desc">High to Low</option>
                <option value="asc">Low to High</option>
              </select>
              <div className="flex items-center space-x-2">
                <input
                  id="screener-filter-name"
                  name="filter_name"
                  type="text"
                  value={filterName}
                  onChange={(e) => setFilterName(e.target.value)}
                  placeholder="Filter name"
                  className="px-3 py-2 border border-gray-300 rounded-md"
                />
                <button
                  onClick={async () => {
                    if (!filterName.trim()) return;
                    try {
                      const resp = await fetch('http://localhost:8000/api/screener/filters/save', {
                        method: 'POST',
                        headers: {
                          'Content-Type': 'application/json',
                          ...(token ? { Authorization: `Bearer ${token}` } : {}),
                        },
                        body: JSON.stringify({ filter_name: filterName.trim(), filter_criteria: filters })
                      });
                      if (resp.ok) {
                        setFilterName('');
                        const data = await resp.json();
                        setSavedFilters(data.filters || []);
                      }
                    } catch (e) { }
                  }}
                  className="px-3 py-2 bg-primary-600 text-white rounded-md"
                >
                  Save
                </button>
              </div>
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Market Cap Category</label>
                <select
                  id="screener-market-cap"
                  name="market_cap_category"
                  multiple
                  value={filters.market_cap_category || []}
                  onChange={(e) => handleFilterChange('market_cap_category', Array.from(e.target.selectedOptions, option => option.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                >
                  {marketCapCategories.map(cat => (
                    <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)} Cap</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">P/E Ratio</label>
                <div className="flex space-x-2">
                  <input
                    id="screener-pe-min"
                    name="pe_ratio_min"
                    type="number"
                    placeholder="Min"
                    value={filters.pe_ratio_min || ''}
                    onChange={(e) => handleFilterChange('pe_ratio_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                  <input
                    id="screener-pe-max"
                    name="pe_ratio_max"
                    type="number"
                    placeholder="Max"
                    value={filters.pe_ratio_max || ''}
                    onChange={(e) => handleFilterChange('pe_ratio_max', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ROE (%)</label>
                <div className="flex space-x-2">
                  <input
                    id="screener-roe-min"
                    name="roe_min"
                    type="number"
                    placeholder="Min"
                    value={filters.roe_min || ''}
                    onChange={(e) => handleFilterChange('roe_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                  <input
                    id="screener-roe-max"
                    name="roe_max"
                    type="number"
                    placeholder="Max"
                    value={filters.roe_max || ''}
                    onChange={(e) => handleFilterChange('roe_max', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Revenue Growth (%)</label>
                <input
                  id="screener-revenue-growth-min"
                  name="revenue_growth_1y_min"
                  type="number"
                  placeholder="Min"
                  value={filters.revenue_growth_1y_min || ''}
                  onChange={(e) => handleFilterChange('revenue_growth_1y_min', e.target.value ? parseFloat(e.target.value) : undefined)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    id="screener-only-nifty50"
                    name="only_nifty50"
                    type="checkbox"
                    checked={filters.only_nifty50 || false}
                    onChange={(e) => handleFilterChange('only_nifty50', e.target.checked)}
                    className="mr-2"
                  />
                  Nifty 50 Only
                </label>
                <label className="flex items-center">
                  <input
                    id="screener-only-nifty100"
                    name="only_nifty100"
                    type="checkbox"
                    checked={filters.only_nifty100 || false}
                    onChange={(e) => handleFilterChange('only_nifty100', e.target.checked)}
                    className="mr-2"
                  />
                  Nifty 100 Only
                </label>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={clearFilters}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Results Summary */}
        <div className="mb-4">
          <p className="text-gray-600">
            Showing {stocks.length} of {totalCount} stocks (Page {currentPage} of {totalPages})
          </p>
        </div>

        {/* Stock Table */}
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Screening stocks...</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Market Cap</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/E</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P/B</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ROE</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">D/E</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Div Yield</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">1Y Return</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Score</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stocks.map((stock) => (
                    <tr key={stock.symbol} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link to={`/stocks/${stock.symbol}`} className="block">
                          <div>
                            <div className="text-sm font-medium text-gray-900 hover:text-primary-700">{stock.symbol}</div>
                            <div className="text-sm text-gray-500">{stock.name}</div>
                            <div className="text-xs text-gray-400">{stock.sector}</div>
                          </div>
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ₹{stock.current_price.toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(stock.market_cap)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.pe_ratio ? stock.pe_ratio.toFixed(1) : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.pb_ratio.toFixed(1)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.roe.toFixed(1)}%
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.debt_to_equity.toFixed(1)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {stock.dividend_yield.toFixed(1)}%
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm ${getChangeColor(stock.price_change_1y)}`}>
                        {formatPercentage(stock.price_change_1y)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">{stock.screener_score}</div>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${stock.screener_score}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-6 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleFilterChange('page', Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50"
              >
                Previous
              </button>
              <span className="text-sm text-gray-700">
                Page {currentPage} of {totalPages}
              </span>
              <button
                onClick={() => handleFilterChange('page', Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-2 border border-gray-300 rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Screener;