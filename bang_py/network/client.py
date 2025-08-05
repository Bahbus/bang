"""Console client for connecting to a Bang websocket server."""

import asyncio
import json
import logging
import ssl

try:  # Optional websockets import for test environments
    from websockets.asyncio.client import connect
    from websockets.exceptions import WebSocketException
    import websockets  # re-exported for tests
except ModuleNotFoundError:  # pragma: no cover - fall back to legacy API
    try:
        import websockets
        from websockets.exceptions import WebSocketException

        connect = websockets.connect
    except ModuleNotFoundError:  # pragma: no cover - handled in main()
        connect = None  # type: ignore[assignment]
        websockets = None  # type: ignore[assignment]
        WebSocketException = Exception  # type: ignore[assignment]

from .server import parse_join_token


async def main(
    uri: str = "ws://localhost:8765",
    room_code: str = "",
    name: str | None = None,
    cafile: str | None = None,
    token: str | None = None,
    token_key: str | None = None,
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
    cafile:
        Optional certificate authority file used to verify the server when
        connecting via ``wss://``.
    token:
        Optional encoded join token. When provided ``uri`` and ``room_code`` are
        derived from the token.
    token_key:
        Key used to decrypt ``token``. If omitted, the default key is used.

    Workflow
    --------
    The client connects to ``uri`` and exchanges the room code and player name.
    Incoming messages are parsed as JSON when possible and printed to the
    console along with the list of players.
    """
    if connect is None:
        logging.error("websockets package is required for networking")
        return

    if token:
        host, port, room_code = parse_join_token(
            token, token_key.encode() if token_key else None
        )
        uri = f"ws://{host}:{port}"

    ssl_ctx = None
    if uri.startswith("wss://") or cafile:
        ssl_ctx = ssl.create_default_context()
        if cafile:
            ssl_ctx.load_verify_locations(cafile)

    async with connect(uri, ssl=ssl_ctx) as websocket:
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
    import argparse

    parser = argparse.ArgumentParser(description="Connect to Bang server")
    parser.add_argument("uri", nargs="?", default="ws://localhost:8765")
    parser.add_argument("--room", default="")
    parser.add_argument("--name", default=None)
    parser.add_argument("--cafile", default=None)
    parser.add_argument("--token", default=None)
    parser.add_argument("--token-key", default=None)
    args = parser.parse_args()

    asyncio.run(
        main(
            args.uri,
            args.room,
            args.name,
            args.cafile,
            args.token,
            args.token_key,
        )
    )


if __name__ == "__main__":
    run()
