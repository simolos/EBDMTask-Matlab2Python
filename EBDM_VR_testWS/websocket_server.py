# websocket_server.py

# Run: pip install numpy websockets uvicorn fastapi

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np
import time

# -------- Config --------
LOG_LEVEL = "INFO"
WS_ROUTE = "/trials"
SAVE_DIR = Path("./session_data")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="EBDM Trial Streaming Server", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="[%(asctime)s] %(levelname)s %(message)s",
)

# ---- Keep track of connected clients ----
active_connections: List[WebSocket] = []

def jsonl_append(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def now_perf() -> float:
    return time.perf_counter()

# ---- Broadcast utility ----
async def broadcast_json(data: dict, sender: Optional[WebSocket] = None):
    """Send JSON to all connected clients except the sender (usually Unity)."""
    dead = []
    for ws in active_connections:
        if ws == sender:
            continue
        try:
            await ws.send_json(data)
        except Exception as e:
            logging.warning("[SRV] Broadcast failed to a client: %s", e)
            dead.append(ws)
    for ws in dead:
        active_connections.remove(ws)

# ---- WebSocket endpoint ----
@app.websocket(WS_ROUTE)
async def trials_ws(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)
    logging.info("[SRV] Client connected (%d total)", len(active_connections))

    try:
        while True:
            msg = await ws.receive()
            if "text" in msg:
                text = msg["text"]
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    logging.warning("[SRV] Invalid JSON: %r", text)
                    continue

                # log & persist
                data["t_recv"] = now_perf()
                jsonl_append(SAVE_DIR / "control_events.jsonl", data)
                logging.info("[SRV] Received: %s", data.get("event_") or data.get("event"))

                # --- BROADCAST to Unity or others ---
                await broadcast_json(data, sender=ws)

                # --- ACK to sender (optional) ---
                await ws.send_json({"event": "ack", "ack_of": data.get("event_") or data.get("event")})

            elif "bytes" in msg:
                logging.warning("[SRV] Binary data ignored in this simplified broadcast server")

    except WebSocketDisconnect:
        active_connections.remove(ws)
        logging.info("[SRV] Client disconnected (%d remaining)", len(active_connections))
    except Exception as e:
        logging.exception("[SRV] Error: %s", e)
        if ws in active_connections:
            active_connections.remove(ws)

@app.get("/")
def root():
    return {"status": "ok", "clients": len(active_connections)}

if __name__ == "__main__":
    uvicorn.run("websocket_server:app", host="0.0.0.0", port=8765, reload=False, log_level="info")
