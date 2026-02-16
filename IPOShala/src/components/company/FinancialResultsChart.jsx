import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const FinancialResultsChart = ({ results }) => {
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const seriesRef = useRef();
    const [metric, setMetric] = useState('revenue'); // 'revenue' or 'profit'

    // Helper to parse date "31-Dec-2024" -> "2024-12-31"
    const parseDate = (dateStr) => {
        if (!dateStr) return null;
        const date = new Date(dateStr);
        if (isNaN(date.getTime())) return null;
        return date.toISOString().split('T')[0];
    };

    // Helper to find value in the nested data array
    const getValue = (dataItems, keys) => {
        if (!dataItems || !Array.isArray(dataItems)) return 0;
        // Common keys for Revenue/Profit in NSE results
        // We search for partial matches in columnName
        const item = dataItems.find(d =>
            keys.some(k => d.columnName && d.columnName.toLowerCase().includes(k.toLowerCase()))
        );
        return item ? parseFloat(item.amount) || 0 : 0;
    };

    useEffect(() => {
        if (!results || results.length === 0 || !chartContainerRef.current) return;

        // Destroy existing chart
        if (chartRef.current) {
            chartRef.current.remove();
        }

        const chart = createChart(chartContainerRef.current, {
            height: 300,
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#333',
                fontFamily: 'Inter, sans-serif',
            },
            grid: {
                vertLines: { visible: false },
                horzLines: { color: '#eef2f6' },
            },
            rightPriceScale: {
                borderVisible: false,
                scaleMargins: {
                    top: 0.1,
                    bottom: 0,
                },
            },
            timeScale: {
                borderVisible: false,
            },
            handleScroll: false,
            handleScale: false,
        });

        const histogramSeries = chart.addHistogramSeries({
            color: metric === 'revenue' ? '#2196f3' : '#4caf50',
        });

        const chartData = results.map(period => {
            const date = parseDate(period.periodEnding);
            let value = 0;

            const details = period.data; // The inner list of line items

            if (metric === 'revenue') {
                value = getValue(details, ['Income from Operations', 'Total Income', 'Revenue']);
            } else {
                value = getValue(details, ['Net Profit', 'Profit for the period', 'Profit/(Loss)']);
            }

            return { time: date, value };
        })
            .filter(d => d.time) // Remove invalid dates
            .sort((a, b) => new Date(a.time) - new Date(b.time)); // Sort chronological

        histogramSeries.setData(chartData);
        chart.timeScale().fitContent();

        chartRef.current = chart;
        seriesRef.current = histogramSeries;

        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            if (chartRef.current) {
                chartRef.current.remove();
            }
            chartRef.current = null;
        };
    }, [results, metric]);

    return (
        <div className="bg-white rounded-xl p-4 border border-gray-200 mb-6">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-semibold text-gray-700">Financial Trend (Quarterly)</h3>
                <div className="flex bg-gray-100 rounded-lg p-1">
                    <button
                        onClick={() => setMetric('revenue')}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${metric === 'revenue' ? 'bg-white shadow-sm text-blue-600' : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Revenue
                    </button>
                    <button
                        onClick={() => setMetric('profit')}
                        className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${metric === 'profit' ? 'bg-white shadow-sm text-green-600' : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Net Profit
                    </button>
                </div>
            </div>
            <div ref={chartContainerRef} className="w-full h-[300px]" />
        </div>
    );
};

export default FinancialResultsChart;
