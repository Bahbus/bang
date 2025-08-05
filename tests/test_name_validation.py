import asyncio
import random

import pytest

pytest.importorskip("cryptography")
from bang_py.network.server import BangServer

websockets = pytest.importorskip("websockets")
try:  # Prefer the modern asyncio API
    from websockets.asyncio.client import connect
    from websockets.asyncio.server import serve
except ModuleNotFoundError:  # pragma: no cover - older websockets versions
    connect = websockets.connect  # type: ignore[attr-defined]
    serve = websockets.serve  # type: ignore[attr-defined]


def test_name_too_long_rejected() -> None:
    async def run_flow() -> None:
        random.seed(0)
        server = BangServer(host="localhost", port=8780, room_code="1234")
        async with serve(server.handler, server.host, server.port):
            async with connect("ws://localhost:8780") as ws:
                await ws.recv()
                await ws.send("1234")
                await ws.recv()
                await ws.send("x" * 21)
                msg = await ws.recv()
                assert msg == "Invalid name"
                with pytest.raises(websockets.exceptions.ConnectionClosed):
                    await ws.recv()
    asyncio.run(run_flow())


def test_name_with_unprintable_rejected() -> None:
    async def run_flow() -> None:
        random.seed(0)
        server = BangServer(host="localhost", port=8781, room_code="1234")
        async with serve(server.handler, server.host, server.port):
            async with connect("ws://localhost:8781") as ws:
                await ws.recv()
                await ws.send("1234")
                await ws.recv()
                await ws.send("bad\x00name")
                msg = await ws.recv()
                assert msg == "Invalid name"
                with pytest.raises(websockets.exceptions.ConnectionClosed):
                    await ws.recv()
    asyncio.run(run_flow())
