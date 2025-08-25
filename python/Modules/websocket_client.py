# websocket_client.py
import asyncio
import json
import logging
from typing import Callable, Dict, Optional, Awaitable
import websockets
from websockets.exceptions import ConnectionClosed  # modern import


class WebSocketClient:
    """
    Async WebSocket client to send and receive trial data.
    """
    def __init__(self, uri: str, on_message: Callable[[Dict], None] | Callable[[Dict], Awaitable[None]], test_dev: bool = False):
        self.uri = uri
        self.on_message = on_message
        self.test_dev = test_dev
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self._recv_task: Optional[asyncio.Task] = None
        self.keep_running = True  # optional if you add auto-reconnect

    async def connect(self):
        # In test mode, do not create real connection
        if self.test_dev:
            logging.info("Test-Dev mode: WebSocket mock activated.")
            return
        logging.info(f"Connecting to WebSocket server at {self.uri}")
        self.ws = await websockets.connect(self.uri)
        # Keep a reference to the receive loop task for clean shutdown
        self._recv_task = asyncio.create_task(self._receive_loop())

    async def _receive_loop(self):
        """Listen for incoming messages and dispatch to callback."""
        try:
            assert self.ws is not None, "Receive loop started without a websocket."
            async for message in self.ws:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logging.warning(f"Non-JSON WS message ignored: {message!r}")
                    continue
                logging.debug(f"Received WS message: {data}")
                # If on_message is async, schedule/await it appropriately
                res = self.on_message(data)
                if asyncio.iscoroutine(res):
                    await res
        except ConnectionClosed as e:
            logging.info(f"WebSocket connection closed: {e}")
        except asyncio.CancelledError:
            # Task cancelled during shutdown
            pass
        except Exception as e:
            logging.exception(f"Error in receive loop: {e}")

    async def send(self, event_type: str, payload: Dict):
        """
        Send a JSON message with given event_type and payload.
        Ensures 'event' key from payload does not override event_type.
        """
        message_dict = {**payload, "event": event_type}  # keep event_type authoritative
        message = json.dumps(message_dict)
        if self.test_dev:
            logging.debug(f"Test-Dev WS send: {message}")
            return
        if not self.ws:
            raise RuntimeError("WebSocket is not connected. Call connect() first.")
        await self.ws.send(message)
        logging.debug(f"Sent WS message: {message}")

    async def close(self):
        """Close the WebSocket connection and cleanup the receive task."""
        self.keep_running = False
        # Cancel receive loop first
        if self._recv_task and not self._recv_task.done():
            self._recv_task.cancel()
            try:
                await self._recv_task
            except asyncio.CancelledError:
                pass
        # Then close the socket
        if self.ws and not self.test_dev:
            try:
                await self.ws.close()
            finally:
                self.ws = None


# Mock implementation for tests
class MockWebSocketClient(WebSocketClient):
    def __init__(self, on_message: Callable[[Dict], None] | Callable[[Dict], Awaitable[None]]):
        super().__init__(uri="", on_message=on_message, test_dev=True)

    async def connect(self):
        logging.info("MockWebSocketClient connected.")

    async def send(self, event_type: str, payload: Dict):
        logging.debug(f"Mock send => event: {event_type}, payload: {payload}")
        # Simulate immediate callback for testing
        await asyncio.sleep(0)
        # Echo back payload as a received message with a response tag
        data = {**payload, "event": f"{event_type}_response"}
        res = self.on_message(data)
        if asyncio.iscoroutine(res):
            await res

    async def close(self):
        logging.info("MockWebSocketClient closed.")
