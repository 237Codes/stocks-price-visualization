import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const category = searchParams.get('category') || 'general'

  const apiKey = process.env.FINNHUB_API_KEY
  const url = `https://finnhub.io/api/v1/news?category=${category}&token=${apiKey}`

  try {
    const response = await fetch(url)
    const data = await response.json()
    return NextResponse.json({ news: data })
  } catch (error) {
    console.error('Error fetching market news:', error)
    return NextResponse.json({ error: 'Failed to fetch market news' }, { status: 500 })
  }
}

