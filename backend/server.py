# server.py
import asyncio
import json
import random
from datetime import datetime
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. Adjust for production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = {
                "time": datetime.utcnow().isoformat() + "Z",
                "price": round(random.uniform(100, 200), 2)
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(1)  # Send data every second
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()
