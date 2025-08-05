import asyncio
import json

import pytest

pytest.importorskip("cryptography")

from bang_py.network.server import BangServer, MAX_MESSAGE_SIZE

websockets = pytest.importorskip("websockets")
try:  # Prefer the modern asyncio API
    from websockets.asyncio.client import connect
    from websockets.asyncio.server import serve
except ModuleNotFoundError:  # pragma: no cover - older websockets versions
    connect = websockets.connect  # type: ignore[attr-defined]
    serve = websockets.serve  # type: ignore[attr-defined]


def test_oversized_message_closes_connection() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=8770, room_code="z999")
        async with serve(server.handler, server.host, server.port, max_size=MAX_MESSAGE_SIZE):
            async with connect("ws://localhost:8770") as ws:
                await ws.recv()
                await ws.send("z999")
                await ws.recv()
                await ws.send("Alice")
                await ws.recv()
                await ws.recv()
                await ws.send("x" * (MAX_MESSAGE_SIZE + 1))
                with pytest.raises(websockets.exceptions.ConnectionClosed) as exc:
                    await ws.recv()
                if hasattr(exc.value, "rcvd"):
                    assert exc.value.rcvd.code == 1009
                else:  # pragma: no cover - older websockets versions
                    assert exc.value.code == 1009
    asyncio.run(run_flow())


def test_malformed_message_ignored() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=8771, room_code="z998")
        async with serve(server.handler, server.host, server.port):
            async with connect("ws://localhost:8771") as ws:
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
        server = BangServer(host="localhost", port=8772, room_code="z997")
        async with serve(server.handler, server.host, server.port):
            async with connect("ws://localhost:8772") as ws:
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
