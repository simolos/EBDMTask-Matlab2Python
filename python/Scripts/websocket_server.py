# server.py
import asyncio
import json
import logging
from typing import Dict, Any, Set
import websockets
from websockets.server import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosed

logging.basicConfig(level=logging.INFO)

class WSServer:
    """
    Simple JSON-based WebSocket server:
      - Expects JSON messages with at least an "event" key
      - Routes events to handlers
      - Sends JSON responses
      - Supports broadcast to all connected clients
    """
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Set[WebSocketServerProtocol] = set()
        self.server = None

    async def start(self):
        # Start the websocket server
        self.server = await websockets.serve(self._handler, self.host, self.port)
        logging.info(f"WebSocket server running at ws://{self.host}:{self.port}")
        # Keep the server alive
        await self.server.wait_closed()

    async def _handler(self, ws: WebSocketServerProtocol):
        # Register client
        self.clients.add(ws)
        client_name = f"{ws.remote_address[0]}:{ws.remote_address[1]}"
        logging.info(f"Client connected: {client_name}")

        # Optional: send a welcome message
        await self._send(ws, event="server_welcome", message="Connected to EBDM server")

        try:
            async for raw in ws:
                # Parse as JSON
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    await self._send(ws, event="error", message="Invalid JSON")
                    continue

                # Ensure "event" exists
                event = data.get("event")
                if not event:
                    await self._send(ws, event="error", message="Missing 'event' field")
                    continue

                # Route to handler
                await self._route_event(ws, event, data)
        except ConnectionClosed:
            logging.info(f"Client disconnected: {client_name}")
        finally:
            # Unregister client
            self.clients.discard(ws)

    async def _route_event(self, ws: WebSocketServerProtocol, event: str, data: Dict[str, Any]):
        """
        Route incoming events to the appropriate handler.
        """
        if event == "ping":
            await self._send(ws, event="pong", ts=data.get("ts"))
        elif event == "trial_update":
            # Example: acknowledge and optionally broadcast
            trial = data.get("trial")
            status = data.get("status")
            await self._send(ws, event="trial_update_ack", trial=trial, status=status)

            # Broadcast to *other* clients that a trial changed
            await self._broadcast(exclude=ws, event="trial_update_broadcast", trial=trial, status=status)
        elif event == "subscribe":
            # Example: keep-alive or marking subscriptions (extend as needed)
            await self._send(ws, event="subscribed", topic=data.get("topic", "all"))
        else:
            # Unknown event
            await self._send(ws, event="error", message=f"Unknown event '{event}'")

    async def _send(self, ws: WebSocketServerProtocol, **payload):
        """
        Send a JSON message to a single client.
        """
        try:
            await ws.send(json.dumps(payload))
        except ConnectionClosed:
            pass

    async def _broadcast(self, exclude: WebSocketServerProtocol | None = None, **payload):
        """
        Send a JSON message to all connected clients (optionally excluding one).
        """
        if not self.clients:
            return
        msg = json.dumps(payload)
        coros = []
        for c in list(self.clients):
            if exclude is not None and c is exclude:
                continue
            coros.append(self._safe_send(c, msg))
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    async def _safe_send(self, ws: WebSocketServerProtocol, msg: str):
        try:
            await ws.send(msg)
        except ConnectionClosed:
            self.clients.discard(ws)

async def main():
    server = WSServer(host="localhost", port=8765)
    # Graceful shutdown handling
    stop = asyncio.Future()

    def _stop_signal():
        if not stop.done():
            stop.set_result(True)

    loop = asyncio.get_running_loop()
    for sig in ("SIGINT", "SIGTERM"):
        try:
            loop.add_signal_handler(getattr(__import__("signal"), sig), _stop_signal)
        except (NotImplementedError, AttributeError):
            # Windows/limited env: fallback—no signal handlers
            pass

    srv_task = asyncio.create_task(server.start())
    await stop  # wait for signal
    # Close the server nicely
    if server.server:
        server.server.close()
        await server.server.wait_closed()
    await srv_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
