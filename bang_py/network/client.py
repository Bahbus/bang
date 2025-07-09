import asyncio
import websockets

async def main(uri: str = "ws://localhost:8765"):
    async with websockets.connect(uri) as websocket:
        greeting = await websocket.recv()
        print(greeting)
        name = input()
        await websocket.send(name)
        response = await websocket.recv()
        print(response)
        async for message in websocket:
            print("Game state:", message)

if __name__ == "__main__":
    asyncio.run(main())
