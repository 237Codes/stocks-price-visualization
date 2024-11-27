import aiohttp
from typing import List, Dict, Optional
from datetime import datetime
from config import API_KEYS

class FinnhubService:
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self):
        self.api_key = API_KEYS["finnhub"]
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def init_session(self):
        if not self.session:
            # Option 1: With proper SSL context
            ssl_context = aiohttp.TCPConnector(ssl=False)
            
            # Option 2 (NOT RECOMMENDED for production): Disable SSL verification
            # ssl_context = aiohttp.TCPConnector(ssl=False)
            
            self.session = aiohttp.ClientSession(
                headers={"X-Finnhub-Token": self.api_key},
                connector=ssl_context
            )
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def get_market_news(self, category: str = "general") -> List[Dict]:
        """
        Get market news
        
        Args:
            category (str): News category. Available values: general, forex, crypto, merger
        
        Raises:
            ValueError: If the API request fails, including the response status and body
        """
        await self.init_session()
        
        # Validate category
        valid_categories = {"general", "forex", "crypto", "merger"}
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        url = f"{self.BASE_URL}/news"
        params = {"category": category}
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                error_body = await response.text()
                raise ValueError(f"API Error: Status {response.status}, Body: {error_body}")
            data = await response.json()
            return data
    
    async def get_company_news(self, symbol: str, 
                             from_date: str, 
                             to_date: str) -> List[Dict]:
        """
        Get company-specific news
        dates format: YYYY-MM-DD
        """
        await self.init_session()
        
        url = f"{self.BASE_URL}/company-news"
        params = {
            "symbol": symbol,
            "from": from_date,
            "to": to_date
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise ValueError(f"API Error: Status {response.status}")
            data = await response.json()
            return data
