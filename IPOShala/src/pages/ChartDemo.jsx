import React, { useState, useEffect } from 'react';
import StockChart from '../components/StockChart';

const ChartDemo = () => {
    const [chartData, setChartData] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Generate mock intraday data (9:15 AM to 3:30 PM)
        const generateMockData = () => {
            const data = [];
            let currentPrice = 210.45;
            const startTime = new Date('2026-02-07T09:15:00');
            const endTime = new Date('2026-02-07T15:30:00');

            let tempTime = new Date(startTime);
            while (tempTime <= endTime) {
                // Random walk for price
                const change = (Math.random() - 0.48) * 0.5; // Slight upward bias
                currentPrice += change;

                data.push({
                    time: tempTime.toISOString().replace('T', ' ').substring(0, 16),
                    value: parseFloat(currentPrice.toFixed(2))
                });

                // Increment by 1 minute
                tempTime.setMinutes(tempTime.getMinutes() + 1);
            }
            return data;
        };

        // Simulate API delay
        const timer = setTimeout(() => {
            setChartData(generateMockData());
            setLoading(false);
        }, 1000);

        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-5xl mx-auto">
                <header className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Intraday Chart Demo</h1>
                    <p className="text-gray-600 mt-2">
                        Testing the reusable StockChart component with TradingView Lightweight Charts.
                    </p>
                </header>

                <main>
                    <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-8">
                        <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                            <h2 className="font-semibold text-gray-800">NSE: E2ERAIL (1m)</h2>
                            <div className="flex space-x-2">
                                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-bold rounded">LIVE</span>
                                <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">Intraday</span>
                            </div>
                        </div>

                        <StockChart
                            data={chartData}
                            loading={loading}
                            title="E2ERAIL"
                            height={500}
                        />
                    </div>

                    <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
                            <h3 className="font-bold text-gray-900 mb-4">Chart Features</h3>
                            <ul className="space-y-3 text-sm text-gray-600">
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                    Area Chart with Gradient Fill
                                </li>
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                    Crosshair tracking with Tooltip
                                </li>
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                    Responsive Design (Auto-resizes)
                                </li>
                                <li className="flex items-center">
                                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                                    Zoom and Pan Support
                                </li>
                            </ul>
                        </div>

                        <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm">
                            <h3 className="font-bold text-gray-900 mb-4">Implementation Details</h3>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                Uses High-performance <strong>lightweight-charts</strong> ES module.
                                Memory leak protection via ResizeObserver cleanup and component unmounting hooks.
                                Accepts time-series objects and auto-sorts for reliable rendering.
                            </p>
                        </div>
                    </section>
                </main>
            </div>
        </div>
    );
};

export default ChartDemo;
