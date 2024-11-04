# server.py
import asyncio
import json
import random
from datetime import datetime, timedelta
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO) 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Adjust for production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/info")
# def info():
#     return {
#         "websocket_endpoint": "/ws/candlestick-data",
#         "data_structure": {
#             "time": "ISO 8601 timestamp",
#             "open": "float",
#             "high": "float",
#             "low": "float",
#             "close": "float"
#         }
#     }

# Initialize starting data for the candlestick
starting_price = 100.0  # Arbitrary starting price
last_price = starting_price
current_time = datetime.utcnow()


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
            logging.info("Sent candlestick data: %s", candlestick_data)
    except Exception as e:
        logging.error(f"Connection error: {e}")
    finally:
        await websocket.close()
        logging.info("Connection closed")
