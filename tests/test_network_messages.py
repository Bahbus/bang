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
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
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


def test_malformed_message_returns_error() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z998")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z998")
                await ws.recv()
                await ws.send("Bob")
                await ws.recv()
                await ws.recv()
                await ws.send("{not-json")
                data = json.loads(await ws.recv())
                assert data["error"]["code"] == "invalid_json"

    asyncio.run(run_flow())


def test_non_object_payload_rejected() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z996")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z996")
                await ws.recv()
                await ws.send("Carl")
                await ws.recv()
                await ws.recv()
                await ws.send(json.dumps([1, 2, 3]))
                data = json.loads(await ws.recv())
                assert data["error"]["code"] == "invalid_message"

    asyncio.run(run_flow())


def test_invalid_payload_rejected() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z997")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z997")
                await ws.recv()
                await ws.send("Eve")
                await ws.recv()
                await ws.recv()
                await ws.send(json.dumps({"action": "draw", "num": "two"}))
                data = json.loads(await ws.recv())
                assert data["error"]["code"] == "invalid_field"

    asyncio.run(run_flow())


def test_unknown_action_rejected() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z995")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z995")
                await ws.recv()
                await ws.send("Dana")
                await ws.recv()
                await ws.recv()
                await ws.send(json.dumps({"action": "unknown"}))
                data = json.loads(await ws.recv())
                assert data["error"]["code"] == "unknown_action"

    asyncio.run(run_flow())


def test_missing_required_field() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z994")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z994")
                await ws.recv()
                await ws.send("Elena")
                await ws.recv()
                await ws.recv()
                await ws.send(json.dumps({"action": "discard"}))
                data = json.loads(await ws.recv())
                assert data["error"]["code"] == "invalid_field"

    asyncio.run(run_flow())


def test_disconnect_cleans_up_connection() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z993")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z993")
                await ws.recv()
                await ws.send("Finn")
                await ws.recv()
                await ws.recv()
            await asyncio.sleep(0)
            assert not server.connections

    asyncio.run(run_flow())


def test_reconnect_after_disconnect() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="z992")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = next(iter(ws_server.sockets)).getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z992")
                await ws.recv()
                await ws.send("Gabe")
                await ws.recv()
                await ws.recv()
            await asyncio.sleep(0)
            assert not server.connections
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("z992")
                await ws.recv()
                await ws.send("Gabe")
                join_msg = await ws.recv()
                assert "Joined game as Gabe" in join_msg
                state = json.loads(await ws.recv())
                assert state["players"][0]["name"] == "Gabe"

    asyncio.run(run_flow())
