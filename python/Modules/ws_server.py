#ws_server.py

import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading

# Create FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/trials")
async def trials_ws(ws: WebSocket):
    await ws.accept()
    # connection exists here, can send JSON inside this coroutine
    while True:
        await asyncio.sleep(1)

def start_server():
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8765, reload=False, log_level="info"), daemon=True).start()
