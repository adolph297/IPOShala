import React, { useMemo } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

const GMPTrendChart = ({ gmpHistory, currentGmp }) => {
    const chartData = useMemo(() => {
        // If no history exists yet, construct a single point based on current GMP
        if (!gmpHistory || gmpHistory.length === 0) {
            if (currentGmp === undefined || currentGmp === null) return [];

            const today = new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
            return [{ date: today, gmp: Number(currentGmp) }];
        }

        // Map history to chart format
        return gmpHistory.map(entry => ({
            date: new Date(entry.date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' }),
            gmp: Number(entry.gmp)
        }));
    }, [gmpHistory, currentGmp]);

    if (chartData.length === 0) {
        return (
            <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm text-center">
                <p className="text-gray-500 text-sm">GMP tracking data is currently unavailable for this IPO.</p>
            </div>
        );
    }

    // Determine trend color
    const latestGmp = chartData[chartData.length - 1]?.gmp || 0;
    const isPositive = latestGmp >= 0;
    const strokeColor = isPositive ? "#16a34a" : "#dc2626"; // green-600 / red-600

    return (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mb-8">
            <div className="text-sm font-semibold bg-[#1a2332] text-white py-3 px-6 flex justify-between items-center">
                <span>Grey Market Premium (GMP) Trend</span>
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${isPositive ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
                    Current: {isPositive ? '+' : ''}₹{latestGmp}
                </span>
            </div>

            <div className="p-6 h-72 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E5E7EB" />
                        <XAxis
                            dataKey="date"
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            dy={10}
                        />
                        <YAxis
                            axisLine={false}
                            tickLine={false}
                            tick={{ fill: '#6B7280', fontSize: 12 }}
                            tickFormatter={(value) => `₹${value}`}
                            dx={-10}
                        />
                        <Tooltip
                            contentStyle={{ borderRadius: '8px', border: '1px solid #E5E7EB', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                            itemStyle={{ color: '#111827', fontWeight: 600 }}
                            formatter={(value) => [`₹${value}`, 'GMP']}
                        />
                        <Line
                            type="monotone"
                            dataKey="gmp"
                            stroke={strokeColor}
                            strokeWidth={3}
                            dot={{ r: 4, strokeWidth: 2, fill: '#fff', stroke: strokeColor }}
                            activeDot={{ r: 6, strokeWidth: 0, fill: strokeColor }}
                            animationDuration={1500}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};

export default GMPTrendChart;
