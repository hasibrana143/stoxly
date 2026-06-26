import React, { useEffect } from 'react';
import { useGetWatchlistQuery, useRemoveFromWatchlistMutation } from '../services/api';
import { Link } from 'react-router-dom';

const Watchlist: React.FC = () => {
    const { data, isLoading, error, refetch } = useGetWatchlistQuery();
    const [removeFromWatchlist] = useRemoveFromWatchlistMutation();

    // Auto-refresh every 30 seconds
    useEffect(() => {
        const interval = setInterval(() => {
            refetch();
        }, 30000);
        return () => clearInterval(interval);
    }, [refetch]);

    const handleRemove = async (id: number) => {
        try {
            await removeFromWatchlist(id).unwrap();
        } catch (err) {
            console.error('Failed to remove from watchlist:', err);
        }
    };

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
                        <span className="block sm:inline"> Failed to load watchlist. Please try again later.</span>
                    </div>
                    <button
                        onClick={() => refetch()}
                        className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    const watchlist = data?.watchlist || [];

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="container mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">My Watchlist</h1>
                        <p className="text-gray-600 mt-1">Track your favorite stocks</p>
                    </div>
                    <button
                        onClick={() => refetch()}
                        className="text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Refresh
                    </button>
                </div>

                {watchlist.length === 0 ? (
                    <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-100">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        <h3 className="text-lg font-medium text-gray-900">Your watchlist is empty</h3>
                        <p className="text-gray-500 mt-2 mb-6">Start tracking stocks to see them here.</p>
                        <Link
                            to="/"
                            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                        >
                            Search Stocks
                        </Link>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {watchlist.map((item) => (
                            <div key={item.id} className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow relative group">
                                <button
                                    onClick={() => handleRemove(item.id)}
                                    className="absolute top-4 right-4 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                                    title="Remove from watchlist"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                    </svg>
                                </button>

                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h3 className="text-lg font-bold text-gray-900">{item.symbol}</h3>
                                        <p className="text-sm text-gray-500 truncate max-w-[200px]">{item.name}</p>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-lg font-bold text-gray-900">₹{item.current_price.toFixed(2)}</p>
                                        <p className={`text-sm font-medium ${item.change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                            {item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
                                        </p>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-50">
                                    <div>
                                        <p className="text-xs text-gray-500">Market Cap</p>
                                        <p className="text-sm font-medium text-gray-900">
                                            {item.market_cap ? `₹${(item.market_cap / 10000000).toFixed(2)} Cr` : 'N/A'}
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-gray-500">P/E Ratio</p>
                                        <p className="text-sm font-medium text-gray-900">{item.pe_ratio ? item.pe_ratio.toFixed(2) : 'N/A'}</p>
                                    </div>
                                </div>

                                <div className="mt-6">
                                    <Link
                                        to={`/stocks/${item.symbol}`}
                                        className="block w-full text-center bg-gray-50 text-indigo-600 py-2 rounded-lg hover:bg-indigo-50 transition-colors font-medium text-sm"
                                    >
                                        View Details
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Watchlist;
