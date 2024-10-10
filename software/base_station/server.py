import asyncio
import websockets

connected = set()

async def echo(websocket, path):
    # Register the client's connection
    connected.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received message from --{websocket.remote_address}-- :'{message}' ")
            # Echo response back to the client
            await websocket.send(f"Echo: {message}")
    finally:
        # Unregister the client's connection
        connected.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    host = "localhost"  # Use '0.0.0.0' if you want to accept connections from any network interface
    port = 8765
    server = await websockets.serve(echo, host, port)
    # Determine the IP and print it with the port
    print(f"WebSocket server started on ws://{host}:{port}")
    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
