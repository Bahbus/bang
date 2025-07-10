import asyncio
import json
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

        async def send_play(idx: int, target: int | None = None) -> None:
            payload = {"action": "play_card", "card_index": idx}
            if target is not None:
                payload["target"] = target
            await websocket.send(json.dumps(payload))

        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                data = message
            print("Game state:", data)


def run() -> None:
    """Entry point for the ``bang-client`` console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
