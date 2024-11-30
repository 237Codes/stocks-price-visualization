'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Newspaper, Bitcoin } from 'lucide-react'

interface NewsItem {
  headline: string
  url: string
  image: string
  summary: string
  datetime: number
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
    <div className="space-y-4">
      {news.map((item, index) => (
        <Card key={index} className="overflow-hidden">
          <CardContent className="p-0">
            <a href={item.url} target="_blank" rel="noopener noreferrer" className="flex flex-col sm:flex-row hover:bg-gray-50 transition-colors">
              <div className="w-full sm:w-1/3 h-48 sm:h-auto relative">
                <img 
                  src={item.image || '/placeholder.svg'} 
                  alt={item.headline}
                  className="absolute inset-0 w-full h-full object-cover"
                />
              </div>
              <div className="p-4 w-full sm:w-2/3">
                <h3 className="font-semibold text-lg mb-2 line-clamp-2">{item.headline}</h3>
                <p className="text-sm text-gray-600 mb-2 line-clamp-3">{item.summary}</p>
                <p className="text-xs text-gray-400">
                  {new Date(item.datetime * 1000).toLocaleString()}
                </p>
              </div>
            </a>
          </CardContent>
        </Card>
      ))}
    </div>
  )

  return (
    <Card className="mt-8">
      <CardContent className="p-6">
        <h2 className="text-2xl font-bold mb-4">Financial News</h2>
        <Tabs defaultValue="market">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="market" className="flex items-center justify-center">
              <Newspaper className="w-4 h-4 mr-2" />
              Market News
            </TabsTrigger>
            <TabsTrigger value="crypto" className="flex items-center justify-center">
              <Bitcoin className="w-4 h-4 mr-2" />
              Crypto News
            </TabsTrigger>
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

