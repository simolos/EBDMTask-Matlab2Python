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

ws = None
@app.websocket("/trials")
async def trials_ws(ws_conn: WebSocket):
    global ws
    await ws_conn.accept()
    ws = ws_conn
    # connection exists here, can send JSON inside this coroutine
    try:
        while True:
            await asyncio.sleep(0.05)
    except Exception as e:
        print(f"[SRV] WebSocket error: {e}")

def start_server():
    threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8765, reload=False, log_level="info"), daemon=True).start()
