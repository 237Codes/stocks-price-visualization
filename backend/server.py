# server.py
import asyncio
import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import aiohttp
from config import API_KEYS, SUPPORTED_SYMBOLS, SUPPORTED_CRYPTO
from services.alpha_vantage import AlphaVantageService
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize starting data for the candlestick
starting_price = 100.0  # Arbitrary starting price
last_price = starting_price
current_time = datetime.utcnow()

class MarketDataManager:
    def __init__(self):
        self.clients = []
        self.finnhub_ws = None
        self.alpha_vantage_session = None
    
    async def connect_client(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)
    
    async def disconnect_client(self, websocket: WebSocket):
        self.clients.remove(websocket)
        await websocket.close()
    
    async def broadcast(self, message: dict):
        dead_clients = []
        for client in self.clients:
            try:
                await client.send_json(message)
            except:
                dead_clients.append(client)
        
        for client in dead_clients:
            self.clients.remove(client)

market_manager = MarketDataManager()

# WebSocket endpoint for streaming candlestick data
@app.websocket("/ws/candlestick-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            global last_price, current_time

            # Simulate candlestick data for one minute intervals
            open_price = last_price
            high_price = open_price + random.uniform(0, 5)  # Random high
            low_price = open_price - random.uniform(0, 5)   # Random low
            close_price = open_price + random.uniform(-2, 2)  # Random close

            # Update last price to the close price of this interval
            last_price = close_price
            candlestick_data = {
                "time": current_time.isoformat() + "Z",
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2)
            }

            # Send the data as JSON to the client
            await websocket.send_text(json.dumps(candlestick_data))

            # Move to the next time interval (e.g., 1 minute)
            current_time += timedelta(minutes=1)
            await asyncio.sleep(1)  # Send data every second for demonstration
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()

@app.websocket("/ws/market-data")
async def market_data_stream(websocket: WebSocket):
    await market_manager.connect_client(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle any client messages if needed
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await market_manager.disconnect_client(websocket)

@app.on_event("startup")
async def startup_event():
    app.state.alpha_vantage = AlphaVantageService()

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, interval: str = "5min"):
    try:
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
            
        if interval not in ["1min", "5min", "15min", "30min", "60min"]:
            raise HTTPException(status_code=400, detail="Invalid interval")
            
        data = await app.state.alpha_vantage.get_stock_data(symbol, interval)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for symbol {symbol}"
            )
        return data
        
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Add logging
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.get("/api/stock/{symbol}/daily")
async def get_daily_stock_data(symbol: str):
    try:
        if not symbol:
            raise HTTPException(status_code=400, detail="Symbol is required")
        
        # Add await here since the method is async
        data = await app.state.alpha_vantage.get_daily_data(symbol)
        if not data or not data.get("data"):
            raise HTTPException(
                status_code=404,
                detail=f"No daily data found for symbol {symbol}"
            )
        return data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error fetching daily data for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stock data"
        )

@app.get("/api/search")
async def search_stocks(
    query: str = Query(..., description="Search query for stock symbols"),
    limit: int = Query(default=10, ge=1, le=100)
):
    """Search for stocks by name or symbol"""
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Search query is required")
            
        results = await app.state.alpha_vantage.search_symbols(query)
        
        # Apply limit
        results = results[:limit]
        
        return {
            "query": query,
            "count": len(results),
            "results": results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error searching stocks: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to search stocks"
        )

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.alpha_vantage.cleanup()

@app.get("/api/stocks")
async def get_stocks(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    exchange: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default="active")
):
    """Get list of available stocks with pagination and filtering"""
    try:
        data = await app.state.alpha_vantage.get_stock_listings()
        stocks = data["stocks"]
        
        # Apply filters
        if exchange:
            stocks = [s for s in stocks if s["exchange"].lower() == exchange.lower()]
        if status:
            stocks = [s for s in stocks if s["status"].lower() == status.lower()]
            
        # Calculate total before pagination
        total = len(stocks)
        
        # Apply pagination
        stocks = stocks[offset:offset + limit]
        
        return {
            "total": total,
            "count": len(stocks),
            "offset": offset,
            "limit": limit,
            "stocks": stocks
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error getting stock listings: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch stock listings"
        )

