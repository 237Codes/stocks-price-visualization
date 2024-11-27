import aiohttp
from typing import List, Dict, Optional, Callable, Set
from datetime import datetime
from config import API_KEYS
import websockets
import json
import asyncio
import ssl  # Add this import at the top

class FinnhubService:
    BASE_URL = "https://finnhub.io/api/v1"
    WS_URL = "wss://ws.finnhub.io"
    
    def __init__(self):
        self.api_key = API_KEYS["finnhub"]
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws_connection = None
        self.subscribed_symbols: Set[str] = set()
        self.message_callback: Optional[Callable] = None
    
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
    
    async def connect_websocket(self, callback: Callable):
        """Initialize WebSocket connection"""
        self.message_callback = callback
        
        while True:
            try:
                # Create SSL context directly from ssl module
                ssl_context = ssl.SSLContext()
                ssl_context.verify_mode = ssl.CERT_NONE
                
                async with websockets.connect(
                    f"{self.WS_URL}?token={self.api_key}",
                    ssl=ssl_context
                ) as websocket:
                    self.ws_connection = websocket
                    
                    # Resubscribe to any previously subscribed symbols
                    for symbol in self.subscribed_symbols:
                        await self.subscribe_symbol(symbol)
                    
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        if self.message_callback:
                            await self.message_callback(data)
                            
            except Exception as e:
                print(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # Wait before reconnecting
    
    async def subscribe_symbol(self, symbol: str):
        """Subscribe to real-time price updates for a symbol"""
        if self.ws_connection:
            subscribe_message = {
                "type": "subscribe",
                "symbol": symbol
            }
            await self.ws_connection.send(json.dumps(subscribe_message))
            self.subscribed_symbols.add(symbol)
    
    async def unsubscribe_symbol(self, symbol: str):
        """Unsubscribe from a symbol's updates"""
        if self.ws_connection:
            unsubscribe_message = {
                "type": "unsubscribe",
                "symbol": symbol
            }
            await self.ws_connection.send(json.dumps(unsubscribe_message))
            self.subscribed_symbols.remove(symbol)
