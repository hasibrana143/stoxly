import React, { useState } from 'react';
import { useOptimizePortfolioMutation } from '../services/api';
import toast from 'react-hot-toast';

const PortfolioOptimizer: React.FC = () => {
  const [symbols, setSymbols] = useState<string[]>(['AAPL', 'GOOGL', 'MSFT']);
  const [newSymbol, setNewSymbol] = useState('');
  const [optimizePortfolio, { isLoading }] = useOptimizePortfolioMutation();
  const [result, setResult] = useState<any>(null);

  const handleOptimize = async () => {
    try {
      const result = await optimizePortfolio({ symbols }).unwrap();
      setResult(result);
      toast.success('Portfolio optimized successfully!');
    } catch (error) {
      toast.error('Optimization failed');
    }
  };

  const addSymbol = () => {
    if (newSymbol && !symbols.includes(newSymbol.toUpperCase())) {
      setSymbols([...symbols, newSymbol.toUpperCase()]);
      setNewSymbol('');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Portfolio Optimizer</h1>
      
      <div className="card mb-8">
        <h2 className="text-xl font-semibold mb-4">Select Stocks</h2>
        <div className="flex gap-4 mb-4">
          <input
            id="optimizer-symbol"
            name="symbol"
            type="text"
            className="input-field"
            placeholder="Add stock symbol"
            value={newSymbol}
            onChange={(e) => setNewSymbol(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addSymbol()}
          />
          <button onClick={addSymbol} className="btn-primary">Add</button>
        </div>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {symbols.map((symbol) => (
            <span key={symbol} className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
              {symbol}
              <button
                onClick={() => setSymbols(symbols.filter(s => s !== symbol))}
                className="ml-2 text-primary-600 hover:text-primary-800"
              >
                ×
              </button>
            </span>
          ))}
        </div>
        
        <button
          onClick={handleOptimize}
          disabled={isLoading || symbols.length < 2}
          className="btn-primary"
        >
          {isLoading ? 'Optimizing...' : 'Optimize Portfolio'}
        </button>
      </div>

      {result && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Optimization Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div>
              <div className="text-sm text-gray-600">Expected Return</div>
              <div className="text-2xl font-bold text-success-600">
                {(result.expected_return * 100).toFixed(2)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Risk (Volatility)</div>
              <div className="text-2xl font-bold text-warning-600">
                {(result.risk * 100).toFixed(2)}%
              </div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Sharpe Ratio</div>
              <div className="text-2xl font-bold text-primary-600">
                {result.sharpe_ratio.toFixed(3)}
              </div>
            </div>
          </div>
          
          <h3 className="text-lg font-semibold mb-4">Recommended Allocation</h3>
          <div className="space-y-3">
            {result.allocation.map((item: any) => (
              <div key={item.symbol} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="font-medium">{item.symbol}</span>
                <span className="font-semibold">{item.percentage.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioOptimizer;
