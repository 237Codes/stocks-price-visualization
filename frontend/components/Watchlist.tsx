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
  const [watchlist, setWatchlist] = useState<Stock[]>([
    { symbol: 'AAPL', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'GOOGL', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'MSFT', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'NVDA', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'TSLA', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'AMZN', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'META', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'ADBE', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'NOW', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'NFLX', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'NIO', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'ZM', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'SQ', price: 0, change: '+0.00', changePercent: '+0.00%' },
    { symbol: 'PYPL', price: 0, change: '+0.00', changePercent: '+0.00%' },
  ])
  const [search, setSearch] = useState('')

  useEffect(() => {
    // Fetch initial stock prices
    watchlist.forEach(updateStockPrice)
  }, [])

  const updateStockPrice = async (stock: Stock) => {
    try {
      const response = await fetch(`/api/stock/${stock.symbol}/intraday?interval=5min`)
      const data = await response.json() as { 'Time Series (5min)': { [key: string]: { '4. close': string, '1. open': string } } }
      
      if (data && data['Time Series (5min)']) {
        const latestData = Object.values(data['Time Series (5min)'])[0]
        const latestPrice = parseFloat(latestData['4. close'])
        const openPrice = parseFloat(latestData['1. open'])
        const change = (latestPrice - openPrice).toFixed(2)
        const changePercent = (((latestPrice - openPrice) / openPrice) * 100).toFixed(2) + '%'

        setWatchlist(prev => 
          prev.map(s => s.symbol === stock.symbol ? { ...s, price: latestPrice, change, changePercent } : s)
        )
      } else {
        console.error('Unexpected data format:', data)
      }
    } catch (error) {
      console.error('Error fetching stock price:', error)
    }
  }

  const addStock = async () => {
    if (search && !watchlist.some(stock => stock.symbol === search.toUpperCase())) {
      const newStock = { symbol: search.toUpperCase(), price: 0, change: '+0.00', changePercent: '+0.00%' }
      setWatchlist(prev => [...prev, newStock])
      await updateStockPrice(newStock)
      setSearch('')
    }
  }

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
              className="flex justify-between items-center py-2 border-b"
              onClick={() => onSelectStock(stock.symbol)}
            >
              <div>
                <div className="font-medium">{stock.symbol}</div>
                <div className="text-sm text-muted-foreground">${stock.price.toFixed(2)}</div>
              </div>
              <div className="text-right">
                <div className={stock.change.startsWith("+") ? "text-green-500" : "text-red-500"}>
                  {stock.change}
                </div>
                <div className={stock.changePercent.startsWith("+") ? "text-green-500 text-sm" : "text-red-500 text-sm"}>
                  {stock.changePercent}
                </div>
              </div>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

