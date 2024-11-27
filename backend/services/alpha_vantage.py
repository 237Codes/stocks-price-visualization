# Setting up Alpha Advantage 
'''

'''

# Alpha vantage service file

import requests
from datetime import datetime
from typing import Dict, List, Optional
from config import API_KEYS
from fastapi import HTTPException
from aiohttp import ClientSession

class AlphaVantageService:
    BASE_URL = "https://www.alphavantage.co/query"
    
    def __init__(self):
        self.api_key = API_KEYS["alpha_vantage"]
        self.session = None
       
    async def close_session(self):
        """Close the aiohttp client session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def get_daily_data(self, symbol: str) -> Dict:
        """Fetch daily stock data using aiohttp"""
        if not self.session:
            self.session = ClientSession()

        try:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": self.api_key
            }
            
            async with self.session.get(self.BASE_URL, params=params, ssl=False) as response:
                data = await response.json()
                
                # Check for error responses
                if "Error Message" in data:
                    raise ValueError(data["Error Message"])
                
                if "Note" in data:
                    raise ValueError(data["Note"])  # API limit message
                    
                # Extract the time series data
                time_series = data.get("Time Series (Daily)")
                if not time_series:
                    raise ValueError(f"No daily data found for symbol {symbol}")
                
                # Convert the data into a more usable format
                formatted_data = [
                    {
                        "date": date,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"]),
                        "volume": int(values["5. volume"])
                    }
                    for date, values in time_series.items()
                ]
                
                # Sort by date (most recent first)
                formatted_data.sort(key=lambda x: x["date"], reverse=True)
                
                return {
                    "symbol": symbol,
                    "data": formatted_data
                }
                
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch data: {str(e)}"
            )
    
    async def search_symbols(self, keywords: str) -> List[Dict]:
        """Search for stock symbols using Alpha Vantage's SYMBOL_SEARCH endpoint"""
        if not self.session:
            self.session = ClientSession()

        try:
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": keywords,
                "apikey": self.api_key
            }
            
            async with self.session.get(self.BASE_URL, params=params, ssl=False) as response:
                data = await response.json()
                
                if "Error Message" in data:
                    raise ValueError(data["Error Message"])
                
                matches = data.get("bestMatches", [])
                
                return [
                    {
                        "symbol": match.get("1. symbol"),
                        "name": match.get("2. name"),
                        "type": match.get("3. type"),
                        "region": match.get("4. region"),
                        "marketOpen": match.get("5. marketOpen"),
                        "marketClose": match.get("6. marketClose"),
                        "timezone": match.get("7. timezone"),
                        "currency": match.get("8. currency"),
                        "matchScore": match.get("9. matchScore")
                    }
                    for match in matches
                ]
                
        except Exception as e:
            print(f"Error searching symbols: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to search symbols: {str(e)}"
            )
    
    async def cleanup(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_stock_listings(self) -> Dict:
        """Fetch list of active stocks from Alpha Vantage"""
        if not self.session:
            self.session = ClientSession()
        
        try:
            params = {
                "function": "LISTING_STATUS",
                "apikey": self.api_key
            }
            
            async with self.session.get(self.BASE_URL, params=params, ssl=False) as response:
                data = await response.json()
                
                if "Error Message" in data:
                    raise ValueError(data["Error Message"])
                
                # Format the response to include only relevant fields
                stocks = [
                    {
                        "symbol": item["symbol"],
                        "name": item["name"],
                        "exchange": item["exchange"],
                        "assetType": item["assetType"],
                        "status": item["status"]
                    }
                    for item in data
                ]
                
                return {
                    "count": len(stocks),
                    "stocks": stocks
                }
                
        except Exception as e:
            print(f"Error fetching stock listings: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch stock listings: {str(e)}"
            )
    
    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> Dict:
        """
        Fetch intraday stock data
        interval options: 1min, 5min, 15min, 30min, 60min
        """
        if not self.session:
            self.session = ClientSession()
        
        try:
            params = {
                "function": "TIME_SERIES_INTRADAY",
                "symbol": symbol,
                "interval": interval,
                "apikey": self.api_key,
                "outputsize": "compact"  # Returns latest 100 data points
            }
            
            async with self.session.get(self.BASE_URL, params=params, ssl=False) as response:
                data = await response.json()
                
                # Check for errors
                if "Error Message" in data:
                    raise ValueError(data["Error Message"])
                if "Note" in data:
                    raise ValueError(data["Note"])
                    
                # Get the time series data
                time_series_key = f"Time Series ({interval})"
                time_series = data.get(time_series_key)
                
                if not time_series:
                    raise ValueError(f"No intraday data found for symbol {symbol}")
                
                # Format the data
                formatted_data = [
                    {
                        "timestamp": timestamp,
                        "open": float(values["1. open"]),
                        "high": float(values["2. high"]),
                        "low": float(values["3. low"]),
                        "close": float(values["4. close"]),
                        "volume": int(values["5. volume"])
                    }
                    for timestamp, values in time_series.items()
                ]
                
                # Sort by timestamp (most recent first)
                formatted_data.sort(key=lambda x: x["timestamp"], reverse=True)
                
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "lastUpdated": datetime.now().isoformat(),
                    "data": formatted_data
                }
                
        except Exception as e:
            print(f"Error fetching intraday data: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch intraday data: {str(e)}"
            )