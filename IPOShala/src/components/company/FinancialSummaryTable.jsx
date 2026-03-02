import React, { useMemo } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const FinancialSummaryTable = ({ ipo }) => {
    // Extract and format financial data from the nested NSE payload
    const financials = useMemo(() => {
        if (!ipo?.nse_company) return [];

        const nse = ipo.nse_company;
        const rawData = nse.audited_financials || [];

        // Sort chronologically if year exists
        const sorted = [...rawData].sort((a, b) => {
            if (!a.year || !b.year) return 0;
            return a.year.toString().localeCompare(b.year.toString());
        });

        return sorted.map((fin, idx) => {
            // Calculate YoY growth metrics if previous year exists
            let revenueGrowth = null;
            let patGrowth = null;

            if (idx > 0) {
                const prev = sorted[idx - 1];
                if (prev.revenue && fin.revenue) {
                    revenueGrowth = ((parseFloat(fin.revenue) - parseFloat(prev.revenue)) / parseFloat(prev.revenue)) * 100;
                }
                if (prev.pat && fin.pat) {
                    patGrowth = ((parseFloat(fin.pat) - parseFloat(prev.pat)) / Math.abs(parseFloat(prev.pat))) * 100;
                }
            }

            return {
                ...fin,
                revenueGrowth,
                patGrowth,
                period: fin.year ? `FY ${fin.year}` : (fin.label || 'Unknown Period')
            };
        }).reverse(); // Latest first for display
    }, [ipo]);

    if (!financials || financials.length === 0) {
        return (
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6 text-center mb-8">
                <p className="text-gray-500 text-sm">Detailed financial summary is currently unavailable for this IPO.</p>
            </div>
        );
    }

    const formatCurrency = (val) => {
        if (!val || val === '-') return '-';
        return `₹${parseFloat(val).toLocaleString('en-IN', { maximumFractionDigits: 2 })} Cr`;
    };

    const GrowthBadge = ({ value }) => {
        if (value === null || value === undefined) return <span className="text-gray-400 text-xs">-</span>;
        const isPositive = value >= 0;
        return (
            <div className={`flex items-center space-x-1 text-xs font-semibold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                <span>{Math.abs(value).toFixed(1)}%</span>
            </div>
        );
    };

    return (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mb-8">
            <div className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 flex justify-between items-center">
                <span>Financial Performance (Consolidated)</span>
                <span className="text-xs font-normal text-gray-300">Values in ₹ Crores</span>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50 uppercase text-xs text-gray-500 tracking-wider">
                        <tr>
                            <th className="px-6 py-4 text-left font-semibold">Period</th>
                            <th className="px-6 py-4 text-right font-semibold">Total Assets</th>
                            <th className="px-6 py-4 text-right font-semibold">Net Worth</th>
                            <th className="px-6 py-4 text-right font-semibold">Total Revenue</th>
                            <th className="px-6 py-4 text-right font-semibold">PAT</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-100">
                        {financials.map((fin, index) => (
                            <tr key={index} className="hover:bg-blue-50/30 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 border-r border-gray-50 bg-gray-50/30">
                                    {fin.period}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">
                                    {formatCurrency(fin.assets || fin.totalAssets)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700 text-right">
                                    {formatCurrency(fin.netWorth)}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right">
                                    <div className="flex flex-col items-end">
                                        <span className="text-sm font-medium text-gray-900">{formatCurrency(fin.revenue || fin.totalRevenue)}</span>
                                        <GrowthBadge value={fin.revenueGrowth} />
                                    </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-right">
                                    <div className="flex flex-col items-end">
                                        <span className="text-sm font-medium text-gray-900">{formatCurrency(fin.pat || fin.profitAftertax)}</span>
                                        <GrowthBadge value={fin.patGrowth} />
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default FinancialSummaryTable;
