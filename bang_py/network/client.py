"""Console client for connecting to a Bang websocket server."""

import asyncio
import json
import logging

try:  # Optional websockets import for test environments
    import websockets
except ModuleNotFoundError:  # pragma: no cover - handled in main()
    websockets = None  # type: ignore[assignment]


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
    if websockets is None:
        logging.error("websockets package is required for networking")
        return

    async with websockets.connect(uri) as websocket:
        prompt = await websocket.recv()
        logging.info(prompt)
        await websocket.send(room_code)
        response = await websocket.recv()
        if response != "Enter your name:":
            logging.info(response)
            return
        logging.info(response)
        if name is None:
            name = input()
        await websocket.send(name)
        join_msg = await websocket.recv()
        logging.info(join_msg)

        async for message in websocket:
            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                data = message
            if isinstance(data, dict):
                msg = data.get("message")
                if msg:
                    logging.info(msg)
                logging.info("Players: %s", data.get("players"))
            else:
                logging.info(str(data))


def run() -> None:
    """Entry point for the ``bang-client`` console script."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
