'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface NewsItem {
  headline: string
  url: string
}

export default function NewsSection() {
  const [marketNews, setMarketNews] = useState<NewsItem[]>([])
  const [cryptoNews, setCryptoNews] = useState<NewsItem[]>([])

  useEffect(() => {
    fetchNews('general', setMarketNews)
    fetchNews('crypto', setCryptoNews)
  }, [])

  const fetchNews = async (category: string, setNews: (news: NewsItem[]) => void) => {
    try {
      const response = await fetch(`/api/news/market?category=${category}`)
      const data = await response.json()
      setNews(data.news.slice(0, 5))
    } catch (error) {
      console.error(`Error fetching ${category} news:`, error)
    }
  }

  const NewsTab = ({ news }: { news: NewsItem[] }) => (
    <ul>
      {news.map((item, index) => (
        <li key={index} className="mb-2">
          <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
            {item.headline}
          </a>
        </li>
      ))}
    </ul>
  )

  return (
    <Card>
      <CardContent>
        <h2 className="text-2xl font-bold mb-4">Financial News</h2>
        <Tabs defaultValue="market">
          <TabsList>
            <TabsTrigger value="market">Market News</TabsTrigger>
            <TabsTrigger value="crypto">Crypto News</TabsTrigger>
          </TabsList>
          <TabsContent value="market">
            <NewsTab news={marketNews} />
          </TabsContent>
          <TabsContent value="crypto">
            <NewsTab news={cryptoNews} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

