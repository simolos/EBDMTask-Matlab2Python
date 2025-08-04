# simple WebSocket server with FastAPI
from fastapi import FastAPI, WebSocket
import uvicorn, json

app = FastAPI()

# list to stocker les messages de la session en cours
events = []

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    print("🔗 Client connected")
    events.clear()
    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            events.append(msg)

            # handle each type
            if msg["type"] == "reaction_time":
                print(f"⏱ Reaction time: {msg['RT']:.4f}s")
            elif msg["type"] == "tap":
                print(f"👆 Tap #{msg['tap_number']} at {msg['timestamp']:.4f}")
            elif msg["type"] == "trial_end":
                # calculate frequency server-side
                # count taps
                n_taps = sum(1 for e in events if e["type"]=="tap")
                # assume fixed duration of 8s
                freq = n_taps / 8.0
                print(f"🏁 Trial ended – {n_taps} taps → {freq:.3f} taps/s")
                # optionally break to close connection
                # break
    except Exception as e:
        print("❌ Client disconnected:", e)

if __name__ == "__main__":
    uvicorn.run("websocket_server:app", host="127.0.0.1", port=8000, log_level="info")
