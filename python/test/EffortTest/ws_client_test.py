# simple WebSocket client to test the server
import asyncio
import websockets

async def test():
    uri = "ws://127.0.0.1:8000/ws"
    # connect to the WebSocket server
    async with websockets.connect(uri) as ws:
        for i in range(5):
            msg = f"test {i}"
            #  send a text message
            await ws.send(msg)
            print("Sent:", msg)
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test())
