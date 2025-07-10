import asyncio
import json
import random
from dataclasses import dataclass
from typing import Dict, List, Any

try:  # Optional websockets import for test environments
    from websockets.server import serve, WebSocketServerProtocol
except ModuleNotFoundError:  # pragma: no cover - handled in start()
    serve = None  # type: ignore[assignment]
    WebSocketServerProtocol = Any  # type: ignore[assignment]

from ..game_manager import GameManager
from ..player import Player, Role

@dataclass
class Connection:
    websocket: WebSocketServerProtocol
    player: Player

def _serialize_players(players: List[Player]) -> List[dict]:
    return [
        {"name": p.name, "health": p.health, "role": p.role.name}
        for p in players
    ]

class BangServer:
    def __init__(self, host: str = "localhost", port: int = 8765, room_code: str | None = None):
        self.host = host
        self.port = port
        self.room_code = room_code or str(random.randint(1000, 9999))
        self.game = GameManager()
        self.connections: Dict[WebSocketServerProtocol, Connection] = {}

    async def handler(self, websocket):
        await websocket.send("Enter room code:")
        code = await websocket.recv()
        if code != self.room_code:
            await websocket.send("Invalid room code")
            return
        await websocket.send("Enter your name:")
        name = await websocket.recv()
        player = Player(name, role=Role.OUTLAW)
        self.game.add_player(player)
        self.connections[websocket] = Connection(websocket, player)
        await websocket.send("Joined game as {}".format(player.name))
        await self.broadcast_players()
        try:
            async for message in websocket:
                if message == "end_turn":
                    self.game.end_turn()
                    await self.broadcast_players()
        finally:
            self.game.players.remove(player)
            del self.connections[websocket]
            await self.broadcast_players()

    async def broadcast_players(self):
        data = json.dumps(_serialize_players(self.game.players))
        for conn in list(self.connections.values()):
            await conn.websocket.send(data)

    async def start(self):
        if serve is None:
            raise RuntimeError(
                "websockets package is required to run the server"
            )
        async with serve(self.handler, self.host, self.port):
            print(
                f"Server started on {self.host}:{self.port} (code: {self.room_code})"
            )
            await asyncio.Future()  # run forever

def main() -> None:
    """Entry point for the ``bang-server`` console script."""
    server = BangServer()
    asyncio.run(server.start())


if __name__ == "__main__":
    main()
