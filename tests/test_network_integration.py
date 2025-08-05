import asyncio
import json
import ssl

import pytest

pytest.importorskip("cryptography")

from bang_py.network.server import BangServer
from bang_py.cards.bang import BangCard

trustme = pytest.importorskip("trustme")

websockets = pytest.importorskip("websockets")
try:  # Prefer the modern asyncio API
    from websockets.asyncio.client import connect
    from websockets.asyncio.server import serve
except ModuleNotFoundError:  # pragma: no cover - older websockets versions
    connect = websockets.connect  # type: ignore[attr-defined]
    serve = websockets.serve  # type: ignore[attr-defined]


def test_server_client_play_flow() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=8767, room_code="1111")
        async with serve(server.handler, server.host, server.port):
            async with connect("ws://localhost:8767") as ws1, connect("ws://localhost:8767") as ws2:
                # Alice join
                await ws1.recv()
                await ws1.send("1111")
                await ws1.recv()
                await ws1.send("Alice")
                await ws1.recv()
                await ws1.recv()
                # Bob join
                await ws2.recv()
                await ws2.send("1111")
                await ws2.recv()
                await ws2.send("Bob")
                await ws2.recv()
                await ws2.recv()

                assert len(server.game.players) == 2
                alice, bob = server.game.players[0], server.game.players[1]
                assert alice.role is None
                assert bob.role is None
                alice.health = 1
                bob.hand.append(BangCard())

                await ws2.send(json.dumps({"action": "play_card", "card_index": 0, "target": 0}))
                data = json.loads(await ws2.recv())
                assert "Bob played" in data["message"]
                data = json.loads(await ws2.recv())
                assert "eliminated" in data["message"]
                assert not alice.is_alive()

asyncio.run(run_flow())


def test_server_client_ssl(tmp_path) -> None:
    ca = trustme.CA()
    server_cert = ca.issue_cert("localhost")
    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    ca_file = tmp_path / "ca.pem"
    server_cert.cert_chain_pems[0].write_to_path(cert)
    server_cert.private_key_pem.write_to_path(key)
    ca.cert_pem.write_to_path(ca_file)

    server = BangServer(
        host="localhost",
        port=8768,
        room_code="2222",
        certfile=str(cert),
        keyfile=str(key),
    )

    async def run_flow() -> None:
        ssl_client = ssl.create_default_context(cafile=str(ca_file))
        async with serve(
            server.handler, server.host, server.port, ssl=server.ssl_context
        ):
            async with connect(
                "wss://localhost:8768", ssl=ssl_client
            ) as ws:
                await ws.recv()
                await ws.send("2222")
                await ws.recv()
                await ws.send("Alice")
                msg = await ws.recv()
                assert "Joined game" in msg

    asyncio.run(run_flow())
