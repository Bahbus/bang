import asyncio
import pytest

pytestmark = pytest.mark.slow

pytest.importorskip("cryptography")

from bang_py.network.server import BangServer  # noqa: E402

websockets = pytest.importorskip("websockets")
from websockets.asyncio.client import connect  # noqa: E402
from websockets.asyncio.server import serve  # noqa: E402


def test_disconnect_cleans_tasks(capsys) -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=0, room_code="3333")
        async with serve(server.handler, server.host, server.port) as ws_server:
            server.port = ws_server.sockets[0].getsockname()[1]
            async with connect(f"ws://localhost:{server.port}") as ws:
                await ws.recv()
                await ws.send("3333")
                await ws.recv()
                await ws.send("Alice")
                await ws.recv()
                await ws.recv()
        await asyncio.sleep(0)

    asyncio.run(run_flow())
    captured = capsys.readouterr()
    assert "Task was destroyed but it is pending" not in captured.err
