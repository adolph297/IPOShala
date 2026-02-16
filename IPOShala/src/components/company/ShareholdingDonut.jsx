import React, { useState, useMemo } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const COLORS = {
    promoter: '#3b82f6', // Blue
    public: '#10b981',   // Green
    employee_trusts: '#f59e0b', // Amber
    fii_dii: '#8b5cf6', // Purple
    other: '#94a3b8' // Gray
};

const MOCK_DATA = {
    promoter: 74.50,
    public: 24.10,
    employee_trusts: 1.40
};

const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }) => {
    return null; // We use legend and tooltip instead of on-chart labels for cleaner look
};

const ShareholdingDonut = ({ data }) => {
    // 1. Normalize Data: Support both single object and historical array
    // Expected formats:
    // - Single: { promoter: 50, public: 50 }
    // - Historical: [ { period: '31-Dec-2024', data: {...} }, ... ] OR { '31-Dec-2024': {...}, ... }

    const formattedData = useMemo(() => {
        if (!data) return [{ period: 'Latest', values: MOCK_DATA, isMock: true }];

        // If array of historical data
        if (Array.isArray(data)) {
            return data.map(d => ({
                period: d.period || d.date || 'Unknown',
                values: d.data || d
            }));
        }

        // If nested object with date keys (check by looking at values)
        const keys = Object.keys(data);
        const firstValue = data[keys[0]];
        if (typeof firstValue === 'object' && firstValue !== null) {
            return keys.map(k => ({
                period: k,
                values: data[k]
            }));
        }

        // Default: Single period
        return [{ period: 'Latest', values: data }];

    }, [data]);

    const [activeIndex, setActiveIndex] = useState(0);

    const currentPeriod = formattedData[activeIndex];
    const chartData = useMemo(() => {
        const values = currentPeriod.values || {};
        const items = [
            { name: 'Promoter & Promoter Group', value: Number(values.promoter || 0), color: COLORS.promoter },
            { name: 'Public', value: Number(values.public || 0), color: COLORS.public },
            { name: 'Employee Trusts', value: Number(values.employee_trusts || 0), color: COLORS.employee_trusts },
            { name: 'FII/DII', value: Number(values.fii_dii || 0), color: COLORS.fii_dii },
            { name: 'Others', value: Number(values.other || 0), color: COLORS.other },
        ].filter(item => item.value > 0);

        // Normalizing to 100% just in case, though usually raw values are fine for Pie
        return items;
    }, [currentPeriod]);

    const totalPercentage = chartData.reduce((acc, curr) => acc + curr.value, 0);

    return (
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
            {/* Header & Tabs */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-4">
                <h3 className="text-lg font-bold text-gray-800">Shareholding Pattern</h3>

                {formattedData.length > 1 && (
                    <div className="flex bg-gray-100 p-1 rounded-lg overflow-x-auto no-scrollbar max-w-full">
                        {formattedData.map((item, index) => (
                            <button
                                key={index}
                                onClick={() => setActiveIndex(index)}
                                className={`px-3 py-1.5 text-xs font-semibold rounded-md whitespace-nowrap transition-all ${index === activeIndex
                                    ? 'bg-white text-blue-600 shadow-sm'
                                    : 'text-gray-500 hover:text-gray-700'
                                    }`}
                            >
                                {item.period}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <div className="flex flex-col md:flex-row items-center gap-8">
                {/* Chart Section */}
                <div className="relative w-[240px] h-[240px] flex-shrink-0">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                innerRadius={50}
                                outerRadius={80}
                                paddingAngle={2}
                                dataKey="value"
                                stroke="none"
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value) => `${value.toFixed(2)}%`}
                                contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                itemStyle={{ color: '#1e293b', fontWeight: 600, fontSize: '12px' }}
                            />
                        </PieChart>
                    </ResponsiveContainer>

                    {/* Centered Mock Badge (if applicable) */}
                    <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                        {currentPeriod.isMock && (
                            <span className="bg-amber-100 text-amber-700 text-[9px] font-bold px-1.5 py-0.5 rounded-full">MOCK</span>
                        )}
                    </div>
                </div>

                {/* Legend Section */}
                <div className="flex-1 w-full space-y-3">
                    {chartData.map((item, index) => (
                        <div key={index} className="flex items-center justify-between group p-2 hover:bg-gray-50 rounded-lg transition-colors">
                            <div className="flex items-center gap-3">
                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                                <span className="text-sm text-gray-600 font-medium group-hover:text-gray-900 transition-colors">{item.name}</span>
                            </div>
                            <span className="text-sm font-bold text-gray-900">{item.value.toFixed(2)}%</span>
                        </div>
                    ))}

                    {chartData.length === 0 && (
                        <div className="text-center text-gray-400 text-sm py-4">No data available for this period.</div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ShareholdingDonut;
