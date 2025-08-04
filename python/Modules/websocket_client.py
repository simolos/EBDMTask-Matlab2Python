# websocket_client.py
import asyncio
import json
import logging
from typing import Callable, Dict
import websockets


class WebSocketClient:
    """
    Async WebSocket client to send and receive trial data.
    """
    def __init__(self, uri: str, on_message: Callable[[Dict], None], test_dev: bool = False):
        self.uri = uri
        self.on_message = on_message
        self.test_dev = test_dev
        self.ws = None
        self.keep_running = True

    async def connect(self):
        if self.test_dev:
            logging.info("Test-Dev mode: WebSocket mock activated.")
            return
        logging.info(f"Connecting to WebSocket server at {self.uri}")
        self.ws = await websockets.connect(self.uri)
        asyncio.create_task(self._receive_loop())

    async def _receive_loop(self):
        """Listen for incoming messages and dispatch to callback."""
        try:
            async for message in self.ws:
                data = json.loads(message)
                logging.debug(f"Received WS message: {data}")
                self.on_message(data)
        except websockets.ConnectionClosed:
            logging.info("WebSocket connection closed.")

    async def send(self, event_type: str, payload: Dict):
        """
        Send a JSON message with given event_type and payload.
        """
        message = json.dumps({"event": event_type, **payload})
        if self.test_dev:
            logging.debug(f"Test-Dev WS send: {message}")
        else:
            await self.ws.send(message)
            logging.debug(f"Sent WS message: {message}")

    async def close(self):
        """Close the WebSocket connection."""
        self.keep_running = False
        if self.ws and not self.test_dev:
            await self.ws.close()


# Mock implementation for tests
class MockWebSocketClient(WebSocketClient):
    def __init__(self, on_message: Callable[[Dict], None]):
        super().__init__(uri="", on_message=on_message, test_dev=True)

    async def connect(self):
        logging.info("MockWebSocketClient connected.")

    async def send(self, event_type: str, payload: Dict):
        logging.debug(f"Mock send => event: {event_type}, payload: {payload}")
        # Simulate immediate callback for testing
        await asyncio.sleep(0)
        # Echo back payload as a received message
        self.on_message({"event": event_type + "_response", **payload})

    async def close(self):
        logging.info("MockWebSocketClient closed.")