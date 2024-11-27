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
        """Search for stock symbols using synchronous requests"""
        try:
            response = requests.get(
                f"{self.BASE_URL}",
                params={
                    "function": "SYMBOL_SEARCH",
                    "keywords": keywords,
                    "apikey": self.api_key
                }
            )
            
            data = response.json()
            
            if "Error Message" in data:
                raise ValueError(data["Error Message"])
                
            matches = data.get("bestMatches", [])
            
            return [
                {
                    "symbol": match.get("1. symbol"),
                    "name": match.get("2. name"),
                    "type": match.get("3. type"),
                    "region": match.get("4. region"),
                    "currency": match.get("8. currency")
                }
                for match in matches
            ]
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch data from Alpha Vantage"
            )
    
    async def cleanup(self):
        if self.session:
            await self.session.close()
            self.session = None
