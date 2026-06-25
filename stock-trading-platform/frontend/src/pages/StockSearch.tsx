import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSearchStocksQuery } from '../services/api';

const StockSearch: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  
  const { data: searchResults } = useSearchStocksQuery(searchQuery, {
    skip: searchQuery.length < 2
  });
  
  

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Stock Search</h1>
      
      <div className="mb-8">
        <input
          id="stock-search-query"
          name="stock_search"
          type="search"
          className="input-field max-w-md"
          placeholder="Search stocks by symbol or name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {searchResults && (
        <div className="card mb-8">
          <h2 className="text-xl font-semibold mb-4">Search Results</h2>
          <div className="grid gap-4">
            {searchResults.stocks.map((stock) => (
              <div
                key={stock.symbol}
                className="p-4 border rounded-lg cursor-pointer hover:bg-gray-50"
                onClick={() => navigate(`/stocks/${stock.symbol}`)}
              >
                <div className="font-semibold">{stock.symbol}</div>
                <div className="text-gray-600 line-clamp-2">{stock.name}</div>
                <div className="text-sm text-gray-500">
                  {stock.sector} • {stock.exchange} • {stock.market_cap_category.toUpperCase()}-CAP
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      
    </div>
  );
};

export default StockSearch;
