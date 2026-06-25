import React, { useState } from 'react';
import { Dialog } from '@headlessui/react';
import { XMarkIcon, PencilIcon, TrashIcon, PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import {
    useListPortfoliosQuery,
    useGetPortfolioDetailsQuery,
    useAddPortfolioItemMutation,
    useDeletePortfolioItemMutation,
    useUpdatePortfolioItemMutation,
    useSearchIndianStocksQuery,
} from '../services/api';

const ManagePortfolio: React.FC = () => {
    const [selectedPortfolioId, setSelectedPortfolioId] = useState<number | null>(null);
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [stockSearchQuery, setStockSearchQuery] = useState('');
    const [selectedStock, setSelectedStock] = useState<any>(null);
    const [quantity, setQuantity] = useState('');
    const [averagePrice, setAveragePrice] = useState('');
    const [editingItem, setEditingItem] = useState<any>(null);

    const { data: portfoliosData } = useListPortfoliosQuery();
    const { data: portfolioDetails } = useGetPortfolioDetailsQuery(selectedPortfolioId!, {
        skip: !selectedPortfolioId,
    });
    const { data: searchResults } = useSearchIndianStocksQuery(
        { query: stockSearchQuery, limit: 10 },
        { skip: stockSearchQuery.length < 2 }
    );

    const [addPortfolioItem, { isLoading: isAdding }] = useAddPortfolioItemMutation();
    const [deletePortfolioItem, { isLoading: isDeleting }] = useDeletePortfolioItemMutation();
    const [updatePortfolioItem, { isLoading: isUpdating }] = useUpdatePortfolioItemMutation();

    const handleAddStock = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedPortfolioId || !selectedStock) return;

        try {
            await addPortfolioItem({
                portfolioId: selectedPortfolioId,
                symbol: selectedStock.symbol,
                quantity: Number(quantity),
                average_price: Number(averagePrice),
            }).unwrap();

            toast.success(`Added ${selectedStock.symbol} to portfolio`);
            setIsAddModalOpen(false);
            resetForm();
        } catch (error) {
            toast.error('Failed to add stock');
        }
    };

    const handleUpdateStock = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedPortfolioId || !editingItem) return;

        try {
            await updatePortfolioItem({
                portfolioId: selectedPortfolioId,
                itemId: editingItem.id,
                quantity: Number(quantity),
                average_price: Number(averagePrice)
            }).unwrap();

            toast.success(`Updated ${editingItem.symbol}`);
            setIsEditModalOpen(false);
            resetForm();
        } catch (error) {
            toast.error('Failed to update stock');
        }
    };

    const handleDeleteStock = async (itemId: number, symbol: string) => {
        if (!selectedPortfolioId) return;
        if (!window.confirm(`Are you sure you want to remove ${symbol} from your portfolio?`)) return;

        try {
            await deletePortfolioItem({
                portfolioId: selectedPortfolioId,
                itemId,
            }).unwrap();

            toast.success(`Removed ${symbol} from portfolio`);
        } catch (error) {
            toast.error('Failed to remove stock');
        }
    };

    const resetForm = () => {
        setStockSearchQuery('');
        setSelectedStock(null);
        setQuantity('');
        setAveragePrice('');
        setEditingItem(null);
    };

    const openEditModal = (item: any) => {
        setEditingItem(item);
        setQuantity(item.quantity);
        setAveragePrice(item.average_price);
        setIsEditModalOpen(true);
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Manage Portfolio</h1>
                <p className="mt-2 text-gray-600">Add, edit, or remove stocks from your portfolio</p>
            </div>

            {/* Portfolio Selector */}
            <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Portfolio</label>
                <select
                    value={selectedPortfolioId || ''}
                    onChange={(e) => setSelectedPortfolioId(Number(e.target.value))}
                    className="block w-full max-w-md px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                >
                    <option value="">Choose a portfolio...</option>
                    {portfoliosData?.portfolios.map((portfolio) => (
                        <option key={portfolio.id} value={portfolio.id}>
                            {portfolio.name}
                        </option>
                    ))}
                </select>
            </div>

            {selectedPortfolioId && portfolioDetails && (
                <>
                    {/* Add Stock Button */}
                    <div className="mb-6">
                        <button
                            onClick={() => setIsAddModalOpen(true)}
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            <PlusIcon className="h-5 w-5 mr-2" />
                            Add Stock
                        </button>
                    </div>

                    {/* Holdings Table */}
                    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Symbol
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Quantity
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Avg Price
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Current Price
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Value
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        P&L
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {portfolioDetails.holdings.map((holding: any) => (
                                    <tr key={holding.id}>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="font-medium text-gray-900">{holding.symbol}</div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {holding.quantity}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            ₹{holding.average_price.toFixed(2)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            ₹{holding.current_price.toFixed(2)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            ₹{holding.current_value.toFixed(2)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className={`text-sm font-medium ${holding.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                                ₹{holding.pnl.toFixed(2)} ({holding.pnl_percent.toFixed(2)}%)
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <button
                                                onClick={() => openEditModal(holding)}
                                                className="text-blue-600 hover:text-blue-900 mr-4"
                                            >
                                                <PencilIcon className="h-5 w-5" />
                                            </button>
                                            <button
                                                onClick={() => handleDeleteStock(holding.id, holding.symbol)}
                                                className="text-red-600 hover:text-red-900"
                                            >
                                                <TrashIcon className="h-5 w-5" />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {/* Add Stock Modal */}
            <Dialog open={isAddModalOpen} onClose={() => { setIsAddModalOpen(false); resetForm(); }} className="relative z-50">
                <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
                <div className="fixed inset-0 flex items-center justify-center p-4">
                    <Dialog.Panel className="mx-auto max-w-md rounded bg-white p-6">
                        <div className="flex justify-between items-center mb-4">
                            <Dialog.Title className="text-lg font-medium">Add Stock</Dialog.Title>
                            <button onClick={() => { setIsAddModalOpen(false); resetForm(); }}>
                                <XMarkIcon className="h-6 w-6 text-gray-400" />
                            </button>
                        </div>

                        <form onSubmit={handleAddStock}>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 mb-2">Search Stock</label>
                                <input
                                    id="manage-portfolio-stock-search"
                                    name="stock_search"
                                    type="search"
                                    value={stockSearchQuery}
                                    onChange={(e) => setStockSearchQuery(e.target.value)}
                                    placeholder="Search by symbol or name..."
                                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                />
                                {stockSearchQuery.length >= 2 && searchResults?.stocks && !selectedStock && (
                                    <div className="absolute z-10 w-full bg-white mt-1 border rounded-md shadow-lg max-h-60 overflow-auto">
                                        {searchResults.stocks.map((stock: any) => (
                                            <div
                                                key={stock.symbol}
                                                className="p-2 hover:bg-gray-100 cursor-pointer"
                                                onClick={() => {
                                                    setSelectedStock(stock);
                                                    setStockSearchQuery(stock.symbol);
                                                }}
                                            >
                                                <div className="font-medium">{stock.symbol}</div>
                                                <div className="text-sm text-gray-500">{stock.name}</div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {selectedStock && (
                                <>
                                    <div className="mb-4">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                                        <input
                                            id="manage-portfolio-quantity"
                                            name="quantity"
                                            type="number"
                                            value={quantity}
                                            onChange={(e) => setQuantity(e.target.value)}
                                            required
                                            min="1"
                                            step="1"
                                            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                        />
                                    </div>

                                    <div className="mb-4">
                                        <label className="block text-sm font-medium text-gray-700 mb-2">Average Price</label>
                                        <input
                                            id="manage-portfolio-average-price"
                                            name="average_price"
                                            type="number"
                                            value={averagePrice}
                                            onChange={(e) => setAveragePrice(e.target.value)}
                                            required
                                            min="0.01"
                                            step="0.01"
                                            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                        />
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={isAdding}
                                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                                    >
                                        {isAdding ? 'Adding...' : 'Add Stock'}
                                    </button>
                                </>
                            )}
                        </form>
                    </Dialog.Panel>
                </div>
            </Dialog>

            {/* Edit Stock Modal */}
            <Dialog open={isEditModalOpen} onClose={() => { setIsEditModalOpen(false); resetForm(); }} className="relative z-50">
                <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
                <div className="fixed inset-0 flex items-center justify-center p-4">
                    <Dialog.Panel className="mx-auto max-w-md rounded bg-white p-6">
                        <div className="flex justify-between items-center mb-4">
                            <Dialog.Title className="text-lg font-medium">Edit {editingItem?.symbol}</Dialog.Title>
                            <button onClick={() => { setIsEditModalOpen(false); resetForm(); }}>
                                <XMarkIcon className="h-6 w-6 text-gray-400" />
                            </button>
                        </div>

                        <form onSubmit={handleUpdateStock}>
                            <div className="mb-4">
                                <label htmlFor="edit-portfolio-quantity" className="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                                <input
                                    id="edit-portfolio-quantity"
                                    name="quantity"
                                    type="number"
                                    value={quantity}
                                    onChange={(e) => setQuantity(e.target.value)}
                                    required
                                    min="1"
                                    step="1"
                                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>

                            <div className="mb-4">
                                <label htmlFor="edit-portfolio-average-price" className="block text-sm font-medium text-gray-700 mb-2">Average Price</label>
                                <input
                                    id="edit-portfolio-average-price"
                                    name="average_price"
                                    type="number"
                                    value={averagePrice}
                                    onChange={(e) => setAveragePrice(e.target.value)}
                                    required
                                    min="0.01"
                                    step="0.01"
                                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isUpdating}
                                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                            >
                                {isUpdating ? 'Updating...' : 'Update Stock'}
                            </button>
                        </form>
                    </Dialog.Panel>
                </div>
            </Dialog>
        </div>
    );
};

export default ManagePortfolio;
