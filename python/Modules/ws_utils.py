# ws_utils.py
# Simple background runner to use an asyncio WebSocket client from sync code.
import asyncio
import threading
import logging
from typing import Callable, Dict, Any
from websocket_client import WebSocketClient

class WSRunner:
    """Run WebSocketClient on a background asyncio loop."""
    def __init__(self, uri: str, on_message: Callable[[Dict[str, Any]], None] | None = None):
        self.uri = uri
        self.on_message = on_message or (lambda msg: logging.debug(f"[WS] {msg}"))
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.client = WebSocketClient(uri=self.uri, on_message=self.on_message)
        self._connected = False

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def start(self):
        """Start background loop and connect the client."""
        if not self.thread.is_alive():
            self.thread.start()
        fut = asyncio.run_coroutine_threadsafe(self.client.connect(), self.loop)
        fut.result()  # wait until connected (fast)
        self._connected = True
        logging.info(f"WS connected to {self.uri}")

    def send(self, event: str, payload: Dict[str, Any]):
        """Fire-and-forget send; safe to call from main PsychoPy thread."""
        if not self._connected:
            logging.warning("WS not connected; dropping message")
            return
        asyncio.run_coroutine_threadsafe(self.client.send(event, payload), self.loop)

    def close(self):
        """Gracefully close client and stop the loop."""
        if self._connected:
            asyncio.run_coroutine_threadsafe(self.client.close(), self.loop).result()
            self._connected = False
        self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread.is_alive():
            self.thread.join(timeout=2)
