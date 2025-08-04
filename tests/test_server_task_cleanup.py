import asyncio
import pytest

pytest.importorskip("cryptography")

from bang_py.network.server import BangServer

websockets = pytest.importorskip("websockets")


def test_disconnect_cleans_tasks(capsys) -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=8789, room_code="3333")
        async with websockets.serve(server.handler, server.host, server.port):
            async with websockets.connect("ws://localhost:8789") as ws:
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
