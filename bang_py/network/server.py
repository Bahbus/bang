import asyncio
import json
import random
from dataclasses import dataclass
from typing import Any, Dict, List

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
    """Return minimal player info for the UI."""
    return [
        {
            "name": p.name,
            "health": p.health,
            "role": p.role.name,
            "equipment": [eq.card_name for eq in p.equipment.values()],
        }
        for p in players
    ]

class BangServer:
    def __init__(self, host: str = "localhost", port: int = 8765, room_code: str | None = None):
        self.host = host
        self.port = port
        self.room_code = room_code or str(random.randint(1000, 9999))
        self.game = GameManager()
        self.connections: Dict[WebSocketServerProtocol, Connection] = {}
        self.game.player_damaged_listeners.append(self._on_player_damaged)
        self.game.player_healed_listeners.append(self._on_player_healed)
        self.game.game_over_listeners.append(self._on_game_over)

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
        await self.broadcast_state()
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                except json.JSONDecodeError:
                    data = message
                if data == "end_turn":
                    self.game.end_turn()
                    await self.broadcast_state()
                elif isinstance(data, dict) and data.get("action") == "draw":
                    num = int(data.get("num", 1))
                    player = self.connections[websocket].player
                    self.game.draw_card(player, num)
                    await self.broadcast_state()
                elif isinstance(data, dict) and data.get("action") == "discard":
                    idx = data.get("card_index")
                    player = self.connections[websocket].player
                    if idx is not None and 0 <= idx < len(player.hand):
                        card = player.hand[idx]
                        self.game.discard_card(player, card)
                        await self.broadcast_state()
                elif isinstance(data, dict) and data.get("action") == "play_card":
                    idx = data.get("card_index")
                    target_idx = data.get("target")
                    player = self.connections[websocket].player
                    if idx is not None and 0 <= idx < len(player.hand):
                        target = None
                        if target_idx is not None:
                            target = self.game._get_player_by_index(target_idx)
                        card = player.hand[idx]
                        self.game.play_card(player, card, target)
                        desc = f"{player.name} played {card.__class__.__name__}"
                        if target:
                            desc += f" on {target.name}"
                        await self.broadcast_state(desc)
        finally:
            self.game.players.remove(player)
            del self.connections[websocket]
            await self.broadcast_state()

    async def broadcast_state(self, message: str | None = None) -> None:
        """Send updated game state to all connected clients."""
        for conn in list(self.connections.values()):
            payload = {
                "players": _serialize_players(self.game.players),
                "hand": [c.card_name for c in conn.player.hand],
            }
            if message:
                payload["message"] = message
            await conn.websocket.send(json.dumps(payload))

    def _on_player_damaged(self, player: Player) -> None:
        msg = (
            f"{player.name} was eliminated"
            if not player.is_alive()
            else f"{player.name} took damage ({player.health})"
        )
        asyncio.create_task(self.broadcast_state(msg))

    def _on_player_healed(self, player: Player) -> None:
        msg = f"{player.name} healed to {player.health}"
        asyncio.create_task(self.broadcast_state(msg))

    def _on_game_over(self, result: str) -> None:
        asyncio.create_task(self.broadcast_state(result))

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
