import React, { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, ChevronLeft, ChevronRight, Filter, X } from 'lucide-react';
import EmptyState from './EmptyState';

const AdvancedTable = ({ columns, data, loading, emptyMessage = "No data found.", emptyType = "default", enableFilters = false }) => {
    const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
    const [filters, setFilters] = useState({ minSize: '', maxSize: '', minGmp: '', minQib: '' });
    const [showMobileFilters, setShowMobileFilters] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(10);

    const parseNum = (str) => {
        if (!str) return 0;
        if (typeof str === 'number') return str;
        const match = str.toString().replace(/,/g, '').match(/[\d.-]+/);
        return match ? parseFloat(match[0]) : 0;
    };

    const filteredData = useMemo(() => {
        if (!enableFilters) return data;

        return data.filter(row => {
            const size = parseNum(row.issue_size || row.issue_information?.issue_size);
            const gmp = parseNum(row.gmp);
            const qib = parseNum(row.subscription?.qib);

            if (filters.minSize && size < Number(filters.minSize)) return false;
            if (filters.maxSize && size > Number(filters.maxSize)) return false;
            if (filters.minGmp && gmp < Number(filters.minGmp)) return false;
            if (filters.minQib && qib < Number(filters.minQib)) return false;

            return true;
        });
    }, [data, filters, enableFilters]);

    const sortedData = useMemo(() => {
        let sortableItems = [...filteredData];
        if (sortConfig.key !== null) {
            sortableItems.sort((a, b) => {
                let aValue = a[sortConfig.key];
                let bValue = b[sortConfig.key];

                // Handle nested or undefined values safely
                if (aValue === undefined || aValue === null) aValue = '';
                if (bValue === undefined || bValue === null) bValue = '';

                if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
                if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
                return 0;
            });
        }
        return sortableItems;
    }, [filteredData, sortConfig]);

    const currentTableData = useMemo(() => {
        const firstPageIndex = (currentPage - 1) * itemsPerPage;
        const lastPageIndex = firstPageIndex + itemsPerPage;
        return sortedData.slice(firstPageIndex, lastPageIndex);
    }, [currentPage, itemsPerPage, sortedData]);

    const totalPages = Math.ceil(sortedData.length / itemsPerPage);

    const handleSort = (key) => {
        let direction = 'asc';
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc';
        }
        setSortConfig({ key, direction });
    };

    const handlePageChange = (page) => {
        setCurrentPage(page);
    };

    const handleFilterChange = (e) => {
        setFilters(prev => ({ ...prev, [e.target.name]: e.target.value }));
        setCurrentPage(1); // reset page on filter change
    };

    const clearFilters = () => {
        setFilters({ minSize: '', maxSize: '', minGmp: '', minQib: '' });
        setCurrentPage(1);
    };

    return (
        <div className="flex flex-col lg:flex-row gap-6 relative">

            {/* Mobile Filter Toggle */}
            {enableFilters && (
                <div className="lg:hidden flex justify-end">
                    <button
                        onClick={() => setShowMobileFilters(!showMobileFilters)}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium shadow-sm hover:bg-blue-700 transition"
                    >
                        <Filter size={16} /> Filters
                    </button>
                </div>
            )}

            {/* Sidebar Filters */}
            {enableFilters && (
                <div className={`w-full lg:w-64 flex-shrink-0 bg-white border border-gray-200 rounded-lg p-5 shadow-sm h-fit ${showMobileFilters ? 'block' : 'hidden lg:block'}`}>
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center gap-2">
                            <Filter size={16} className="text-blue-500" />
                            Advanced Filters
                        </h3>
                        {showMobileFilters && (
                            <button onClick={() => setShowMobileFilters(false)} className="lg:hidden text-gray-500 hover:text-gray-700">
                                <X size={20} />
                            </button>
                        )}
                    </div>

                    <div className="space-y-5">
                        {/* Issue Size */}
                        <div>
                            <label className="block text-xs font-semibold text-gray-600 mb-2">Issue Size (Cr)</label>
                            <div className="flex items-center gap-2">
                                <input
                                    type="number"
                                    name="minSize"
                                    placeholder="Min"
                                    value={filters.minSize}
                                    onChange={handleFilterChange}
                                    className="w-1/2 px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                                />
                                <span className="text-gray-400">-</span>
                                <input
                                    type="number"
                                    name="maxSize"
                                    placeholder="Max"
                                    value={filters.maxSize}
                                    onChange={handleFilterChange}
                                    className="w-1/2 px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                                />
                            </div>
                        </div>

                        {/* Minimum GMP */}
                        <div>
                            <label className="block text-xs font-semibold text-gray-600 mb-2">Minimum GMP (₹)</label>
                            <input
                                type="number"
                                name="minGmp"
                                placeholder="e.g. 50"
                                value={filters.minGmp}
                                onChange={handleFilterChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            />
                        </div>

                        {/* QIB Subscription */}
                        <div>
                            <label className="block text-xs font-semibold text-gray-600 mb-2">QIB Subscription (Min x)</label>
                            <input
                                type="number"
                                name="minQib"
                                placeholder="e.g. 10"
                                value={filters.minQib}
                                onChange={handleFilterChange}
                                className="w-full px-3 py-2 border border-gray-300 rounded text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            />
                        </div>

                        {/* Reset Buttons */}
                        <div className="pt-4 border-t border-gray-100 flex gap-2">
                            <button onClick={clearFilters} className="w-full py-2 bg-gray-100 text-gray-700 text-sm font-medium rounded hover:bg-gray-200 transition">
                                Clear All
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Table Area */}
            <div className="flex-1 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden flex flex-col min-w-0">
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-[#1a2332]">
                            <tr>
                                {columns.map((col, idx) => (
                                    <th
                                        key={idx}
                                        onClick={() => col.sortable !== false && handleSort(col.accessor)}
                                        className={`px-6 py-4 text-left text-xs font-semibold text-white uppercase tracking-wider ${col.sortable !== false ? 'cursor-pointer hover:bg-[#2a3442] transition-colors' : ''} ${col.className || ''}`}
                                    >
                                        <div className="flex items-center space-x-1">
                                            <span>{col.header}</span>
                                            {col.sortable !== false && sortConfig.key === col.accessor && (
                                                <span className="text-gray-400">
                                                    {sortConfig.direction === 'asc' ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                                                </span>
                                            )}
                                        </div>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {loading ? (
                                <tr>
                                    <td colSpan={columns.length} className="px-6 py-8 text-center text-sm text-gray-500">
                                        <div className="flex justify-center items-center space-x-2">
                                            <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                                            <span>Loading real-time data...</span>
                                        </div>
                                    </td>
                                </tr>
                            ) : currentTableData.length === 0 ? (
                                <tr>
                                    <td colSpan={columns.length} className="p-0">
                                        <EmptyState
                                            type={emptyType}
                                            message={emptyMessage}
                                            actionText="Clear Filters"
                                            actionLink="#"
                                        />
                                    </td>
                                </tr>
                            ) : (
                                currentTableData.map((row, rowIndex) => (
                                    <tr key={row.id || rowIndex} className="hover:bg-gray-50 transition-colors duration-150">
                                        {columns.map((col, colIndex) => (
                                            <td key={colIndex} className={`px-6 py-4 whitespace-nowrap text-sm ${col.cellClassName || 'text-gray-700'}`}>
                                                {col.render ? col.render(row) : row[col.accessor]}
                                            </td>
                                        ))}
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Controls */}
                {!loading && sortedData.length > 0 && (
                    <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
                        <div className="flex items-center text-sm text-gray-500">
                            <span>Show</span>
                            <select
                                title="Items per page"
                                aria-label="Items per page"
                                className="mx-2 bg-white border border-gray-300 rounded-md py-1 px-2 focus:outline-none focus:ring-1 focus:ring-blue-500"
                                value={itemsPerPage}
                                onChange={(e) => {
                                    setItemsPerPage(Number(e.target.value));
                                    setCurrentPage(1); // Reset to first page
                                }}
                            >
                                <option value={10}>10</option>
                                <option value={20}>20</option>
                                <option value={50}>50</option>
                            </select>
                            <span>entries</span>
                        </div>

                        <div className="flex items-center space-x-2 text-sm">
                            <span className="text-gray-500 hidden sm:block">
                                Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, sortedData.length)} of {sortedData.length} entries
                            </span>
                            <div className="flex items-center space-x-1 ml-4 border border-gray-300 rounded-md overflow-hidden bg-white">
                                <button
                                    onClick={() => handlePageChange(currentPage - 1)}
                                    disabled={currentPage === 1}
                                    className="px-2 py-1 text-gray-500 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed border-r border-gray-300 transition-colors"
                                    aria-label="Previous Page"
                                >
                                    <ChevronLeft size={16} />
                                </button>

                                <span className="px-4 py-1 font-medium text-gray-700 border-r border-gray-300 min-w-[3rem] text-center">
                                    {currentPage}
                                </span>

                                <button
                                    onClick={() => handlePageChange(currentPage + 1)}
                                    disabled={currentPage === totalPages || totalPages === 0}
                                    className="px-2 py-1 text-gray-500 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                    aria-label="Next Page"
                                >
                                    <ChevronRight size={16} />
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdvancedTable;
