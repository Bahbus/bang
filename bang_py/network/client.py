import asyncio
import websockets

async def main(uri: str = "ws://localhost:8765", room_code: str = "", name: str | None = None):
    async with websockets.connect(uri) as websocket:
        prompt = await websocket.recv()
        print(prompt)
        await websocket.send(room_code)
        response = await websocket.recv()
        if response != "Enter your name:":
            print(response)
            return
        print(response)
        if name is None:
            name = input()
        await websocket.send(name)
        join_msg = await websocket.recv()
        print(join_msg)
        async for message in websocket:
            print("Game state:", message)

if __name__ == "__main__":
    asyncio.run(main())
