import React, { useEffect, useRef, memo } from 'react';
import { Card, CardContent } from '@/components/ui/card';

interface StockChartProps {
  symbol: string;
}

function StockChart({ symbol }: StockChartProps) {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (container.current) {
      container.current.innerHTML = ''; // Clear previous widget
      const script = document.createElement("script");
      script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
      script.type = "text/javascript";
      script.async = true;
      script.innerHTML = `
        {
          "autosize": true,
          "symbol": "${symbol}",
          "interval": "D",
          "timezone": "Etc/UTC",
          "theme": "dark",
          "style": "1",
          "locale": "en",
          "allow_symbol_change": true,
          "hotlist": true,
          "calendar": false,
          "support_host": "https://www.tradingview.com"
        }`;
      container.current.appendChild(script);
    }
  }, [symbol]);

  return (
    <Card className="mb-8 bg-white text-black" style={{ height: '65%', width: '100%' }}>
      <CardContent style={{ height: '95%', width: '100%' }}>
        <h2 className="text-2xl font-bold mb-4">{symbol} Stock Price</h2>
        <div className="tradingview-widget-container" ref={container} style={{ height: '70vh', width: '100%' }}>
          <div className="tradingview-widget-container__widget" style={{ height: '100%', width: '100%' }}></div>
          <div className="tradingview-widget-copyright">
            <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">
              <span className="blue-text">Track all markets on TradingView</span>
            </a>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default memo(StockChart);