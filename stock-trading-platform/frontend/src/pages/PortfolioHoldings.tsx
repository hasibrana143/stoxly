import React from 'react';
import { useGetPortfolioHoldingsQuery } from '../services/api';
import { Link } from 'react-router-dom';

const PortfolioHoldings: React.FC = () => {
    const { data, isLoading, error } = useGetPortfolioHoldingsQuery();

    if (isLoading) {
        return (
            <div className="min-h-screen bg-gray-50">
                <div className="flex justify-center items-center h-[calc(100vh-64px)]">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50">
                <div className="container mx-auto px-4 py-8">
                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                        <strong className="font-bold">Error!</strong>
                        <span className="block sm:inline"> Failed to load portfolio holdings. Please try again later.</span>
                    </div>
                    <div className="flex gap-4">
                        <button
                            onClick={() => window.location.reload()}
                            className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition-colors"
                        >
                            Retry
                        </button>
                        <Link
                            to="/portfolio"
                            className="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300 transition-colors"
                        >
                            Back to Portfolio
                        </Link>
                    </div>
                </div>
            </div>
        );
    }

    const holdings = data?.holdings || [];
    const totalValue = holdings.reduce((sum, h) => sum + h.current_value, 0);
    const totalInvestment = holdings.reduce((sum, h) => sum + h.investment_value, 0);
    const totalPnL = totalValue - totalInvestment;
    const totalPnLPercent = totalInvestment > 0 ? (totalPnL / totalInvestment) * 100 : 0;

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Portfolio Holdings</h1>
                        <p className="text-gray-600 mt-1">Manage your stock investments</p>
                    </div>
                    <Link
                        to="/portfolio"
                        className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                        Manage Portfolios
                    </Link>
                </div>

                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500">Current Value</h3>
                        <p className="text-2xl font-bold text-gray-900 mt-2">₹{totalValue.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500">Invested Amount</h3>
                        <p className="text-2xl font-bold text-gray-900 mt-2">₹{totalInvestment.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500">Total P&L</h3>
                        <p className={`text-2xl font-bold mt-2 ${totalPnL >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {totalPnL >= 0 ? '+' : ''}₹{Math.abs(totalPnL).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                        </p>
                    </div>
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-sm font-medium text-gray-500">Return</h3>
                        <p className={`text-2xl font-bold mt-2 ${totalPnLPercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {totalPnLPercent >= 0 ? '+' : ''}{totalPnLPercent.toFixed(2)}%
                        </p>
                    </div>
                </div>

                {/* Holdings Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stock</th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Avg Price</th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">LTP</th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Current Value</th>
                                    <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
                                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Portfolio</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {holdings.length === 0 ? (
                                    <tr>
                                        <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                                            No holdings found. Start investing to see your portfolio here.
                                        </td>
                                    </tr>
                                ) : (
                                    holdings.map((holding, index) => (
                                        <tr key={`${holding.portfolio_id}-${holding.symbol}-${index}`} className="hover:bg-gray-50 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex items-center">
                                                    <div>
                                                        <div className="text-sm font-medium text-gray-900">{holding.symbol}</div>
                                                        <div className="text-sm text-gray-500">{holding.name}</div>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">{holding.quantity}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">₹{holding.average_price.toFixed(2)}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">₹{holding.current_price.toFixed(2)}</td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium text-gray-900">
                                                ₹{holding.current_value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right">
                                                <div className={`text-sm font-medium ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    {holding.pnl >= 0 ? '+' : ''}₹{Math.abs(holding.pnl).toFixed(2)}
                                                </div>
                                                <div className={`text-xs ${holding.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                    ({holding.pnl_percent >= 0 ? '+' : ''}{holding.pnl_percent.toFixed(2)}%)
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{holding.portfolio_name}</td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PortfolioHoldings;
