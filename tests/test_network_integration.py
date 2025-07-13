import asyncio
import json

import pytest
from bang_py.network.server import BangServer
from bang_py.cards.bang import BangCard

websockets = pytest.importorskip("websockets")


def test_server_client_play_flow() -> None:
    async def run_flow() -> None:
        server = BangServer(host="localhost", port=8767, room_code="1111")
        async with websockets.serve(server.handler, server.host, server.port):
            async with websockets.connect("ws://localhost:8767") as ws1, \
                       websockets.connect("ws://localhost:8767") as ws2:
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
                alice.health = 1
                bob.hand.append(BangCard())

                await ws2.send(json.dumps({"action": "play_card", "card_index": 0, "target": 0}))
                data = json.loads(await ws2.recv())
                assert "Bob played" in data["message"]
                data = json.loads(await ws2.recv())
                assert "eliminated" in data["message"]
                assert not alice.is_alive()

    asyncio.run(run_flow())
