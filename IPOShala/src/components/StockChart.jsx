import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType } from 'lightweight-charts';

const StockChart = ({
    data,
    loading = false,
    title = "Intraday Chart",
    height = 400
}) => {
    const chartContainerRef = useRef();
    const chartRef = useRef();
    const seriesRef = useRef();
    const tooltipRef = useRef();

    useEffect(() => {
        if (!chartContainerRef.current) return;

        // Initialize Chart
        const chart = createChart(chartContainerRef.current, {
            height: height,
            layout: {
                background: { type: ColorType.Solid, color: '#ffffff' },
                textColor: '#333',
                fontSize: 12,
                fontFamily: 'Inter, Roboto, sans-serif',
            },
            grid: {
                vertLines: { color: '#f0f3fa' },
                horzLines: { color: '#f0f3fa' },
            },
            crosshair: {
                mode: 1, // Magnet
                vertLine: {
                    width: 1,
                    color: '#2196f3',
                    style: 2, // Dashed
                    labelBackgroundColor: '#2196f3',
                },
                horzLine: {
                    width: 1,
                    color: '#2196f3',
                    style: 2, // Dashed
                    labelBackgroundColor: '#2196f3',
                },
            },
            rightPriceScale: {
                borderColor: '#f0f3fa',
            },
            timeScale: {
                borderColor: '#f0f3fa',
                timeVisible: true,
                secondsVisible: false,
            },
            handleScroll: true,
            handleScale: true,
        });

        // Create Area Series (NSE Style)
        const areaSeries = chart.addAreaSeries({
            lineColor: '#2196f3',
            topColor: 'rgba(33, 150, 243, 0.4)',
            bottomColor: 'rgba(33, 150, 243, 0.0)',
            lineWidth: 2,
        });

        chartRef.current = chart;
        seriesRef.current = areaSeries;

        // Responsive Resize
        const handleResize = () => {
            chart.applyOptions({ width: chartContainerRef.current.clientWidth });
        };

        window.addEventListener('resize', handleResize);

        // ResizeObserver for more robust resizing
        const resizeObserver = new ResizeObserver(() => {
            handleResize();
        });
        resizeObserver.observe(chartContainerRef.current);

        // Tooltip Implementation
        chart.subscribeCrosshairMove(param => {
            if (
                param.point === undefined ||
                !param.time ||
                param.point.x < 0 ||
                param.point.x > chartContainerRef.current.clientWidth ||
                param.point.y < 0 ||
                param.point.y > height
            ) {
                tooltipRef.current.style.display = 'none';
            } else {
                const dataPoint = param.seriesData.get(areaSeries);
                const price = dataPoint.value !== undefined ? dataPoint.value : dataPoint.close;
                const time = param.time;

                tooltipRef.current.style.display = 'block';
                tooltipRef.current.innerHTML = `
          <div style="font-weight: 600; color: #333">${title}</div>
          <div style="font-size: 14px; margin: 4px 0;">₹ ${price.toFixed(2)}</div>
          <div style="color: #666; font-size: 11px;">${time}</div>
        `;

                const coordinate = areaSeries.priceToCoordinate(price);
                let shiftedCoordinate = param.point.x - 50;
                if (shiftedCoordinate < 0) shiftedCoordinate = 0;
                if (shiftedCoordinate > chartContainerRef.current.clientWidth - 100) {
                    shiftedCoordinate = chartContainerRef.current.clientWidth - 100;
                }

                tooltipRef.current.style.left = shiftedCoordinate + 'px';
                tooltipRef.current.style.top = (coordinate - 80) + 'px';
            }
        });

        return () => {
            window.removeEventListener('resize', handleResize);
            resizeObserver.disconnect();
            chart.remove();
        };
    }, [height, title]);

    useEffect(() => {
        if (seriesRef.current && data && data.length > 0) {
            // Sort data by time to ensure lightweight-charts doesn't throw error
            const sortedData = [...data].sort((a, b) => {
                const timeA = typeof a.time === 'string' ? new Date(a.time).getTime() : a.time;
                const timeB = typeof b.time === 'string' ? new Date(b.time).getTime() : b.time;
                return timeA - timeB;
            });

            // Format time to unix timestamp if needed, or string "YYYY-MM-DD"
            // lightweight-charts expects unix timestamp (seconds) or "YYYY-MM-DD"
            const formattedData = sortedData.map(item => ({
                time: typeof item.time === 'string' ? Math.floor(new Date(item.time).getTime() / 1000) : item.time,
                value: item.value
            }));

            seriesRef.current.setData(formattedData);
            chartRef.current.timeScale().fitContent();
        }
    }, [data]);

    return (
        <div style={{ position: 'relative', width: '100%', padding: '20px', background: '#fff', borderRadius: '8px', border: '1px solid #f0f3fa' }}>
            {loading && (
                <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.8)', zIndex: 10 }}>
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
            )}

            {!loading && (!data || data.length === 0) && (
                <div style={{ height: height, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#666' }}>
                    No intraday data available
                </div>
            )}

            <div ref={chartContainerRef} style={{ width: '100%', height: height }} />

            <div
                ref={tooltipRef}
                style={{
                    display: 'none',
                    position: 'absolute',
                    width: '120px',
                    padding: '8px',
                    background: 'white',
                    border: '1px solid #2196f3',
                    borderRadius: '4px',
                    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
                    zIndex: 100,
                    pointerEvents: 'none',
                    textAlign: 'center'
                }}
            />
        </div>
    );
};

export default StockChart;
