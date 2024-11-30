'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface StockChartProps {
  symbol: string
}

// Define the expected structure of 'values'
interface TimeSeriesValues {
  '4. close': string;
}

export default function StockChart({ symbol }: StockChartProps) {
  const [data, setData] = useState<{ time: string; price: number }[]>([])

  useEffect(() => {
    fetchStockData()
  }, [symbol])

  const fetchStockData = async () => {
    try {
      const response = await fetch(`/api/stock/${symbol}/intraday?interval=5min`)
      const result = await response.json()
      const chartData = Object.entries(result['Time Series (5min)']).map(([time, values]) => {
        const typedValues = values as TimeSeriesValues; // Type assertion
        return {
          time,
          price: parseFloat(typedValues['4. close'] || '0'),
        };
      }).reverse()
      setData(chartData)
    } catch (error) {
      console.error('Error fetching stock data:', error)
    }
  }

  return (
    <Card className="mb-8">
      <CardContent>
        <h2 className="text-2xl font-bold mb-4">{symbol} Stock Price</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="price" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}

