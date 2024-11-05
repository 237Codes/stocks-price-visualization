import React, { useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';

const CandlestickChart = () => {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const candlestickSeriesRef = useRef(null);

    useEffect(() => {
        // Create the chart
        chartRef.current = createChart(chartContainerRef.current, {
            width: chartContainerRef.current.clientWidth,
            height: 400,
            layout: {
                backgroundColor: '#ffffff',
                textColor: '#000000',
            },
            grid: {
                vertLines: { color: '#eeeeee' },
                horzLines: { color: '#eeeeee' },
            },
            priceScale: {
                borderColor: '#cccccc',
            },
            timeScale: {
                borderColor: '#cccccc',
                timeVisible: true,
            },
        });

        // Create candlestick series
        candlestickSeriesRef.current = chartRef.current.addCandlestickSeries({
            upColor: '#4CAF50', // Green for up
            downColor: '#FF5252', // Red for down
            borderVisible: true,
            wickUpColor: '#4CAF50',
            wickDownColor: '#FF5252',
        });

        // Clean up the chart on component unmount
        return () => {
            chartRef.current.remove();
        };
    }, []);

    useEffect(() => {
        // Establish WebSocket connection to the backend
        const ws = new WebSocket('ws://localhost:8000/ws/candlestick-data');

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);

            // Add new candlestick to the series
            candlestickSeriesRef.current.update({
                time: new Date(message.time).getTime() / 1000, // Convert timestamp to seconds
                open: message.open,
                high: message.high,
                low: message.low,
                close: message.close,
            });
        };

        // Close WebSocket connection on component unmount
        return () => {
            ws.close();
        };
    }, []);

    return <div ref={chartContainerRef} style={{ position: 'relative', width: '100%', height: '400px' }} />;
};

export default CandlestickChart;
