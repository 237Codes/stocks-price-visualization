'use client'

import { useState } from 'react'
import Watchlist from '../components/Watchlist'
import StockChart from '../components/StockChart'
import NewsSection from '../components/NewsSection'

export default function Home() {
  const [selectedStock, setSelectedStock] = useState('AAPL')

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold mb-8">Stock Visualizer</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <Watchlist onSelectStock={setSelectedStock} />
        <div className="md:col-span-2">
          <StockChart symbol={selectedStock} />
          <NewsSection />
        </div>
      </div>
    </div>
  )
}

