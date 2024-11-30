'use client'

import { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface Stock {
  symbol: string
  price: number
  change: string
  changePercent: string
}

interface WatchlistProps {
  onSelectStock: (symbol: string) => void
}

export default function Watchlist({ onSelectStock }: WatchlistProps) {
  const [watchlist, setWatchlist] = useState<Stock[]>(() => {
    if (typeof window !== 'undefined') {
      const savedWatchlist = localStorage.getItem('watchlist');
      return savedWatchlist ? JSON.parse(savedWatchlist) : [];
    }
    return [];
  });
  const [search, setSearch] = useState('');
  const [selectedStock, setSelectedStock] = useState<string | null>(null);
  const [actionStock, setActionStock] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      if (watchlist.length === 0) {
        const defaultSymbols = ['AAPL', 'GOOGL', 'MSFT', 'NVDA', 'TSLA', 'AMZN', 'META', 'ADBE', 'NOW', 'NFLX', 'NIO', 'ZM', 'SQ', 'PYPL'];
        const defaultWatchlist = defaultSymbols.map(symbol => ({
          symbol,
          price: 0,
          change: '+0.00',
          changePercent: '+0.00%'
        }));
        setWatchlist(defaultWatchlist);
        defaultWatchlist.forEach(updateStockPrice);
      } else {
        watchlist.forEach(updateStockPrice);
      }
    }
  }, []);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('watchlist', JSON.stringify(watchlist));
    }
  }, [watchlist]);

  const updateStockPrice = async (stock: Stock) => {
    try {
      const apiKey = process.env.ALPHA_VANTAGE_API_KEY;
      const response = await fetch(`https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=${stock.symbol}&apikey=${apiKey}`);
      const data = await response.json();

      console.log(`Data for ${stock.symbol}:`, data); // Log the response data

      if (data && data['Global Quote']) {
        const latestPrice = parseFloat(data['Global Quote']['05. price']);
        const change = data['Global Quote']['09. change'];
        const changePercent = data['Global Quote']['10. change percent'];

        setWatchlist(prevWatchlist => prevWatchlist.map(s => 
          s.symbol === stock.symbol 
            ? { ...s, price: latestPrice, change, changePercent } 
            : s
        ));
      } else {
        console.warn(`No data found for ${stock.symbol}`);
      }
    } catch (error) {
      console.error(`Error fetching data for ${stock.symbol}:`, error);
    }
  };

  const addStock = async () => {
    if (search && !watchlist.some(stock => stock.symbol === search.toUpperCase())) {
      const newStock = { symbol: search.toUpperCase(), price: 0, change: '+0.00', changePercent: '+0.00%' };
      setWatchlist(prev => [...prev, newStock]);
      await updateStockPrice(newStock);
      setSearch('');
    }
  };

  const removeStock = (symbol: string) => {
    setWatchlist(prevWatchlist => prevWatchlist.filter(stock => stock.symbol !== symbol));
  };

  const handleSelectStock = (symbol: string) => {
    setSelectedStock(symbol);
    onSelectStock(symbol);
  };

  const handleStockClick = (symbol: string) => {
    setActionStock(symbol === actionStock ? null : symbol);
  };

  return (
    <Card>
      <CardContent>
        <h2 className="text-xl font-semibold mb-4">Watchlist</h2>
        <div className="flex mb-4">
          <Input
            type="text"
            placeholder="Add stock symbol"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="mr-2"
          />
          <Button onClick={addStock}>Add</Button>
        </div>
        <ul>
          {watchlist.map((stock) => (
            <li
              key={stock.symbol}
              className={`flex justify-between items-center py-2 border-b ${selectedStock === stock.symbol ? 'bg-blue-100' : ''}`}
              onClick={() => handleStockClick(stock.symbol)}
            >
              <div>
                <div className="font-medium">{stock.symbol}</div>
                <div className="text-sm text-muted-foreground">${stock.price.toFixed(2)}</div>
              </div>
              <div className="text-right">
                <div className={parseFloat(stock.change) >= 0 ? "text-green-500" : "text-red-500"}>
                  {stock.change}
                </div>
                <div className={parseFloat(stock.changePercent) >= 0 ? "text-green-500 text-sm" : "text-red-500 text-sm"}>
                  {stock.changePercent}
                </div>
              </div>
              {actionStock === stock.symbol && (
                <div className="flex space-x-2">
                  <Button onClick={() => handleSelectStock(stock.symbol)} className="ml-4">Set as Current</Button>
                  <Button onClick={() => removeStock(stock.symbol)} className="ml-4">Remove</Button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

