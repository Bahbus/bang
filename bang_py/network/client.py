import asyncio
import json
import websockets


async def main(
    uri: str = "ws://localhost:8765", room_code: str = "", name: str | None = None
) -> None:
    """Connect to a ``bang-server`` instance and handle basic interaction.

    Parameters
    ----------
    uri:
        WebSocket URI of the running server.
    room_code:
        Code required to join the game. If empty the prompt from the server is
        shown and the code can be entered interactively.
    name:
        Optional player name. If ``None``, the user is prompted for it.

    Workflow
    --------
    The client connects to ``uri`` and exchanges the room code and player name.
    Incoming messages are parsed as JSON when possible and printed to the
    console along with the list of players.
    """
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
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                data = message
            if isinstance(data, dict):
                msg = data.get("message")
                if msg:
                    print(msg)
                print("Players:", data.get("players"))
            else:
                print(data)


def run() -> None:
    """Entry point for the ``bang-client`` console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
