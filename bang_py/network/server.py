import asyncio
import json
import secrets
from dataclasses import dataclass
from typing import Any, Dict, List

try:  # Optional websockets import for test environments
    from websockets.server import serve, WebSocketServerProtocol
except ModuleNotFoundError:  # pragma: no cover - handled in start()
    serve = None  # type: ignore[assignment]
    WebSocketServerProtocol = Any  # type: ignore[assignment]

from ..game_manager import GameManager
from ..player import Player
from ..cards.roles import OutlawRoleCard
from ..characters.jesse_jones import JesseJones
from ..characters.jose_delgado import JoseDelgado
from ..characters.kit_carlson import KitCarlson
from ..characters.lucky_duke import LuckyDuke
from ..characters.pat_brennan import PatBrennan
from ..characters.pedro_ramirez import PedroRamirez
from ..characters.vera_custer import VeraCuster
from ..cards.general_store import GeneralStoreCard


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
            "role": p.role.card_name,
            "equipment": [eq.card_name for eq in p.equipment.values()],
        }
        for p in players
    ]


class BangServer:
    """Run a websocket server for a single Bang game and manage clients."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8765,
        room_code: str | None = None,
        expansions: list[str] | None = None,
        max_players: int = 7,
    ) -> None:
        self.host = host
        self.port = port
        # Generate a random 4-digit room code using a cryptographically
        # secure RNG to avoid predictable codes.
        self.room_code = room_code or f"{secrets.randbelow(9000) + 1000:04d}"
        self.game = GameManager(expansions=expansions or [])
        self.connections: Dict[WebSocketServerProtocol, Connection] = {}
        self.max_players = max_players
        self.game.player_damaged_listeners.append(self._on_player_damaged)
        self.game.player_healed_listeners.append(self._on_player_healed)
        self.game.game_over_listeners.append(self._on_game_over)
        self.game.turn_started_listeners.append(self._on_turn_started)

    async def handler(self, websocket: WebSocketServerProtocol) -> None:
        """Register a new client and process game commands sent over the socket."""
        await websocket.send("Enter room code:")
        code = await websocket.recv()
        if code != self.room_code:
            await websocket.send("Invalid room code")
            return
        await websocket.send("Enter your name:")
        name = await websocket.recv()
        if len(self.game.players) >= self.max_players:
            await websocket.send("Game full")
            return
        player = Player(name, role=OutlawRoleCard())
        player.metadata.auto_miss = True
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
                        if isinstance(card, GeneralStoreCard):
                            player.hand.pop(idx)
                            self.game.discard_pile.append(card)
                            names = self.game.start_general_store(player)
                            desc = f"{player.name} played {card.__class__.__name__}"
                            await self.broadcast_state(desc)
                            order = self.game.general_store_order or []
                            if order:
                                first = order[0]
                                conn = self._find_connection(first)
                                if conn:
                                    payload = json.dumps({
                                        "prompt": "general_store",
                                        "cards": names,
                                    })
                                    asyncio.create_task(conn.websocket.send(payload))
                        else:
                            self.game.play_card(player, card, target)
                            desc = f"{player.name} played {card.__class__.__name__}"
                            if target:
                                desc += f" on {target.name}"
                            await self.broadcast_state(desc)
                elif isinstance(data, dict) and data.get("action") == "general_store_pick":
                    idx = data.get("index")
                    player = self.connections[websocket].player
                    if isinstance(idx, int) and self.game.general_store_cards is not None:
                        if self.game.general_store_pick(player, idx):
                            await self.broadcast_state()
                            if self.game.general_store_cards is not None:
                                nxt = self.game.general_store_order[self.game.general_store_index]
                                conn = self._find_connection(nxt)
                                if conn:
                                    payload = json.dumps(
                                        {
                                            "prompt": "general_store",
                                            "cards": [
                                                c.card_name
                                                for c in self.game.general_store_cards
                                            ],
                                        }
                                    )
                                    asyncio.create_task(conn.websocket.send(payload))
                elif isinstance(data, dict) and data.get("action") == "use_ability":
                    ability = data.get("ability")
                    player = self.connections[websocket].player
                    if ability == "sid_ketchum":
                        idxs = data.get("indices") or []
                        self.game.sid_ketchum_ability(player, idxs)
                    elif ability == "chuck_wengam":
                        self.game.chuck_wengam_ability(player)
                    elif ability == "doc_holyday":
                        idxs = data.get("indices") or []
                        self.game.doc_holyday_ability(player, idxs)
                    elif ability == "vera_custer":
                        idx = data.get("target")
                        target = None
                        if idx is not None:
                            target = self.game._get_player_by_index(idx)
                        if target:
                            self.game.vera_custer_copy(player, target)
                    elif ability == "jesse_jones":
                        idx = data.get("target")
                        card_idx = data.get("card_index")
                        target = self.game._get_player_by_index(idx) if idx is not None else None
                        self.game.draw_phase(player, jesse_target=target, jesse_card=card_idx)
                    elif ability == "kit_carlson":
                        discard = data.get("discard")
                        cards = player.metadata.kit_cards
                        player.metadata.kit_cards = None
                        if isinstance(cards, list) and cards:
                            for i, card in enumerate(cards):
                                if i == discard:
                                    self.game.discard_pile.append(card)
                                else:
                                    player.hand.append(card)
                        else:
                            self.game.draw_phase(player, kit_back=discard)
                    elif ability == "pedro_ramirez":
                        use_discard = bool(data.get("use_discard", True))
                        self.game.draw_phase(player, pedro_use_discard=use_discard)
                    elif ability == "jose_delgado":
                        eq_idx = data.get("equipment")
                        self.game.draw_phase(player, jose_equipment=eq_idx)
                    elif ability == "pat_brennan":
                        idx = data.get("target")
                        card = data.get("card")
                        target = self.game._get_player_by_index(idx) if idx is not None else None
                        self.game.draw_phase(player, pat_target=target, pat_card=card)
                    elif ability == "lucky_duke":
                        idx = data.get("card_index", 0)
                        cards = player.metadata.lucky_cards or []
                        player.metadata.lucky_cards = []
                        if cards:
                            chosen = cards[idx] if idx < len(cards) else cards[0]
                            player.hand.append(chosen)
                            for i, c in enumerate(cards):
                                if c is not chosen:
                                    self.game.discard_pile.append(c)
                            self.game.draw_card(player)
                        else:
                            self.game.draw_phase(player)
                    elif ability == "uncle_will":
                        cidx = data.get("card_index")
                        if cidx is not None and 0 <= cidx < len(player.hand):
                            card = player.hand[cidx]
                            if self.game.uncle_will_ability(player, card):
                                await self.broadcast_state()
                                continue
                    await self.broadcast_state()
                elif isinstance(data, dict) and data.get("action") == "set_auto_miss":
                    enabled = bool(data.get("enabled", True))
                    self.connections[websocket].player.metadata.auto_miss = enabled
                    await self.broadcast_state()
        finally:
            self.game.remove_player(player)
            self.connections.pop(websocket, None)
            await self.broadcast_state()

    async def broadcast_state(self, message: str | None = None) -> None:
        """Send updated game state to all connected clients."""
        for websocket, conn in list(self.connections.items()):
            payload = {
                "players": _serialize_players(self.game.players),
                "hand": [c.card_name for c in conn.player.hand],
                "character": getattr(conn.player.character, "name", ""),
                "event": getattr(self.game.current_event, "name", ""),
            }
            if message:
                payload["message"] = message
            try:
                await conn.websocket.send(json.dumps(payload))
            except Exception:
                # Remove the player from the game if their websocket is no
                # longer reachable before dropping the connection entirely.
                try:
                    await conn.websocket.close()
                except Exception:
                    pass
                self.game.remove_player(conn.player)
                self.connections.pop(websocket, None)

    def _find_connection(self, player: Player) -> Connection | None:
        for conn in self.connections.values():
            if conn.player is player:
                return conn
        return None

    def _on_turn_started(self, player: Player) -> None:
        conn = self._find_connection(player)
        if not conn:
            return
        if isinstance(player.character, VeraCuster):
            options = [
                {"index": i, "name": p.character.name}
                for i, p in enumerate(self.game.players)
                if p is not player and p.is_alive()
            ]
            if options:
                payload = json.dumps({"prompt": "vera", "options": options})
                asyncio.create_task(conn.websocket.send(payload))
            return

        if player.metadata.awaiting_draw:
            player.metadata.awaiting_draw = False
            if isinstance(player.character, JesseJones):
                targets = [
                    {"index": i, "name": p.name}
                    for i, p in enumerate(self.game.players)
                    if p is not player and p.hand
                ]
                if targets:
                    payload = json.dumps({"prompt": "jesse_jones", "targets": targets})
                    asyncio.create_task(conn.websocket.send(payload))
                else:
                    self.game.draw_phase(player)
                    asyncio.create_task(self.broadcast_state())
                return

            if isinstance(player.character, KitCarlson):
                cards = [self.game.deck.draw() for _ in range(3)]
                player.metadata.kit_cards = [c for c in cards if c]
                names = [c.card_name for c in player.metadata.kit_cards or []]
                payload = json.dumps({"prompt": "kit_carlson", "cards": names})
                asyncio.create_task(conn.websocket.send(payload))
                return

            if isinstance(player.character, PedroRamirez):
                if self.game.discard_pile:
                    payload = json.dumps({"prompt": "pedro_ramirez"})
                    asyncio.create_task(conn.websocket.send(payload))
                else:
                    self.game.draw_phase(player, pedro_use_discard=False)
                    asyncio.create_task(self.broadcast_state())
                return

            if isinstance(player.character, JoseDelgado):
                equips = [
                    {"index": i, "name": c.card_name}
                    for i, c in enumerate(player.hand)
                    if hasattr(c, "slot")
                ]
                if equips:
                    payload = json.dumps({"prompt": "jose_delgado", "equipment": equips})
                    asyncio.create_task(conn.websocket.send(payload))
                else:
                    self.game.draw_phase(player)
                    asyncio.create_task(self.broadcast_state())
                return

            if isinstance(player.character, PatBrennan):
                targets = []
                for i, p in enumerate(self.game.players):
                    if p is player or not p.equipment:
                        continue
                    targets.append(
                        {
                            "index": i,
                            "cards": [c.card_name for c in p.equipment.values()],
                        }
                    )
                if targets:
                    payload = json.dumps({"prompt": "pat_brennan", "targets": targets})
                    asyncio.create_task(conn.websocket.send(payload))
                else:
                    self.game.draw_phase(player)
                    asyncio.create_task(self.broadcast_state())
                return

            if isinstance(player.character, LuckyDuke):
                cards = [self.game.deck.draw(), self.game.deck.draw()]
                player.metadata.lucky_cards = [c for c in cards if c]
                names = [c.card_name for c in player.metadata.lucky_cards or []]
                if names:
                    payload = json.dumps({"prompt": "lucky_duke", "cards": names})
                    asyncio.create_task(conn.websocket.send(payload))
                else:
                    self.game.draw_phase(player)
                    asyncio.create_task(self.broadcast_state())
                return

    def _on_player_damaged(self, player: Player, _src: Player | None = None) -> None:
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

    async def start(self) -> None:
        """Start the websocket server and run until cancelled."""
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
