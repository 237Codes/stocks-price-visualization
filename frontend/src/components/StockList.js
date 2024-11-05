// StockList.js

import React, { useEffect, useState } from "react";
import StockChart from "./StockChart";

const StockList = () => {
    const [stocks, setStocks] = useState([]);
    const [selectedSymbol, setSelectedSymbol] = useState(null);
    const [priceData, setPriceData] = useState([]);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws/prices");

        socket.onmessage = (event) => {
            const stockUpdate = JSON.parse(event.data);
            setStocks((prevStocks) => {
                const updatedStocks = prevStocks.filter(
                    (s) => s.symbol !== stockUpdate.symbol
                );
                return [...updatedStocks, stockUpdate];
            });

            // For the candlestick chart, generate OHLC data
            if (selectedSymbol === stockUpdate.symbol) {
                const newCandle = {
                    time: new Date(stockUpdate.timestamp).getTime() / 1000,
                    open: stockUpdate.price * 0.99,    // mock example for demonstration
                    high: stockUpdate.price * 1.01,
                    low: stockUpdate.price * 0.98,
                    close: stockUpdate.price,
                };
                setPriceData((prevData) => [...prevData, newCandle]);
            }
        };

        socket.onopen = () => {
            console.log("WebSocket connection established.");
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed.");
        };

        return () => socket.close();
    }, [selectedSymbol]);

    return (
        <div>
            <h2>Live Stock and Crypto Prices</h2>
            <ul>
                {stocks.map((stock) => (
                    <li key={stock.symbol}>
                        <strong>{stock.symbol}:</strong> ${stock.price} (Last Updated: {stock.timestamp})
                        <button onClick={() => {
                            setSelectedSymbol(stock.symbol);
                            setPriceData([]); // Clear previous data when changing symbol
                        }}>
                            View Chart
                        </button>
                    </li>
                ))}
            </ul>

            {selectedSymbol && (
                <StockChart symbol={selectedSymbol} priceData={priceData} />
            )}
        </div>
    );
};

export default StockList;
