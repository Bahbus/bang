import asyncio
import json

import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("cryptography")

from bang_py.network.server import BangServer, MAX_MESSAGE_SIZE  # noqa: E402

websockets = pytest.importorskip("websockets")
from websockets.asyncio.client import connect  # noqa: E402
from websockets.asyncio.server import serve  # noqa: E402


def test_oversized_message_closes_connection() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z999")
        async with serve(
            server.handler, server.host, server.port, max_size=MAX_MESSAGE_SIZE
        ) as ws_server:
            server.port = ws_server.sockets[0].getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z999")
                await ws.recv()
                await ws.send("Alice")
                await ws.recv()
                await ws.recv()
                await ws.send("x" * (MAX_MESSAGE_SIZE + 1))
                with pytest.raises(websockets.exceptions.ConnectionClosed) as exc:
                    await ws.recv()
                assert exc.value.rcvd.code == 1009

    asyncio.run(run_flow())


def test_malformed_message_ignored() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z998")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = ws_server.sockets[0].getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z998")
                await ws.recv()
                await ws.send("Bob")
                await ws.recv()
                await ws.recv()
                await ws.send("{not-json")
                # Connection should remain open
                await ws.send("end_turn")
                data = json.loads(await ws.recv())
                assert "players" in data

    asyncio.run(run_flow())


def test_invalid_payload_rejected() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z997")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = ws_server.sockets[0].getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z997")
                await ws.recv()
                await ws.send("Eve")
                await ws.recv()
                await ws.recv()
                await ws.send(json.dumps({"action": "draw", "num": "two"}))
                data = json.loads(await ws.recv())
                assert data.get("error") == "invalid message"

    asyncio.run(run_flow())
