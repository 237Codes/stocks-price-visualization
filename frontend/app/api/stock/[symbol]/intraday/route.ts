import { NextResponse } from 'next/server';

export async function GET(request: Request, context: { params: { symbol: string } }) {
  const { params } = context; // Await the params in the context if necessary
  const { symbol } = params; // Ensure symbol is accessed correctly

  if (!symbol) {
    return NextResponse.json({ error: 'Stock symbol is required' }, { status: 400 });
  }

  const { searchParams } = new URL(request.url);
  const interval = searchParams.get('interval') || '5min';

  const apiKey = process.env.ALPHA_VANTAGE_API_KEY;
  const url = `https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=${symbol}&interval=${interval}&apikey=${apiKey}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data?.Note || 'Error fetching data from Alpha Vantage');
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching intraday data:', error);
    return NextResponse.json({ error: 'Failed to fetch intraday data' }, { status: 500 });
  }
}
