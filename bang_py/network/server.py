"""Websocket server implementation for hosting a Bang game."""

from __future__ import annotations

import asyncio
import json
import secrets
import ssl
from collections.abc import Coroutine, Sequence, Mapping
from dataclasses import dataclass, field
from typing import Any, cast
import logging

from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import WebSocketException

from ..game_manager import GameManager
from ..game_manager_protocol import GameManagerProtocol
from ..player import Player
from ..cards.general_store import GeneralStoreCard
from .messages import (
    DiscardPayload,
    DrawPayload,
    PlayCardPayload,
    SetAutoMissPayload,
    UseAbilityPayload,
)
from .token_utils import _token_key_bytes, generate_join_token, parse_join_token
from .validation import validate_player_name

logger = logging.getLogger(__name__)

# Maximum allowed size for incoming websocket messages
MAX_MESSAGE_SIZE = 4096

__all__ = ["BangServer", "generate_join_token", "parse_join_token", "validate_player_name"]


# Use slots to reduce memory footprint and prevent dynamic attribute assignment.
@dataclass(slots=True)
class Connection:
    websocket: ServerConnection
    player: Player
    task_group: asyncio.TaskGroup = field(default_factory=asyncio.TaskGroup)


def _serialize_players(players: Sequence[Player]) -> list[dict]:
    """Return minimal player info for the UI."""
    return [
        {
            "name": p.name,
            "health": p.health,
            "role": "" if p.role is None else p.role.card_name,
            "character": getattr(p.character, "name", ""),
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
        certfile: str | None = None,
        keyfile: str | None = None,
        token_key: bytes | str | None = None,
    ) -> None:
        self.host = host
        self.port = port
        # Generate a random six-character room code using a cryptographically
        # secure RNG to avoid predictable codes.
        self.room_code = room_code or secrets.token_hex(3)
        self.game: GameManagerProtocol = GameManager(expansions=expansions or [])
        self.token_key = _token_key_bytes(token_key)
        self.connections: dict[ServerConnection, Connection] = {}
        self.max_players = max_players
        self.certfile = certfile
        self.keyfile = keyfile
        self.ssl_context: ssl.SSLContext | None = None
        if certfile:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(certfile, keyfile)
        self._broadcast_group: asyncio.TaskGroup | None = None
        self.game.player_damaged_listeners.append(self._on_player_damaged)
        self.game.player_healed_listeners.append(self._on_player_healed)
        self.game.game_over_listeners.append(self._on_game_over)
        self.game.turn_started_listeners.append(self._on_turn_started)

    def generate_join_token(self) -> str:
        """Return an encoded join token for this server."""

        return generate_join_token(self.host, self.port, self.room_code, self.token_key)

    def _create_send_task(self, conn: Connection, payload: str | Mapping[str, object]) -> None:
        """Create a supervised task to send ``payload``.

        ``payload`` may be a JSON string or a mapping that will be serialized.
        """

        payload_str = payload if isinstance(payload, str) else json.dumps(payload)

        async def _send() -> None:
            try:
                await conn.websocket.send(payload_str)
            except asyncio.CancelledError as exc:  # pragma: no cover - network
                logger.warning("Send to %s cancelled", conn.player.name, exc_info=exc)
                raise
            except WebSocketException as exc:  # pragma: no cover - network
                logger.exception("Send to %s failed", conn.player.name, exc_info=exc)

        conn.task_group.create_task(_send())

    def _spawn_broadcast(self, coro: Coroutine[Any, Any, Any]) -> None:
        if self._broadcast_group is not None:
            self._broadcast_group.create_task(coro)
        else:  # pragma: no cover - server not started
            asyncio.create_task(coro)

    async def handler(self, websocket: ServerConnection) -> None:
        """Register a new client and process game commands sent over the socket."""

        await websocket.send("Enter room code:")
        code = await websocket.recv()
        if code != self.room_code:
            await websocket.send("Invalid room code")
            return

        await websocket.send("Enter your name:")
        raw_name = await websocket.recv()
        name = raw_name.decode() if isinstance(raw_name, bytes) else raw_name
        if not validate_player_name(name):
            await websocket.send("Invalid name")
            return
        name = name.strip()
        if len(self.game.players) >= self.max_players:
            await websocket.send("Game full")
            return

        player = Player(name)
        player.metadata.auto_miss = True
        conn = Connection(websocket, player)
        self.connections[websocket] = conn

        async def client_loop() -> None:
            try:
                async for message in websocket:
                    if len(message) > MAX_MESSAGE_SIZE:
                        await websocket.close(code=1009, reason="Message too large")
                        break
                    await self._process_message(websocket, message)
            finally:
                self.game.remove_player(player)
                self.connections.pop(websocket, None)
                await self.broadcast_state()

        async with conn.task_group as tg:
            self.game.add_player(player)
            await websocket.send(f"Joined game as {player.name}")
            await self.broadcast_state()
            tg.create_task(client_loop())

    def _validate_payload(self, payload: dict[str, object]) -> bool:
        """Validate that ``payload`` conforms to the expected schema."""
        action = payload.get("action")
        if not isinstance(action, str):
            return False

        schemas: dict[str, dict[str, tuple[type, ...]]] = {
            "draw": {"num": (int,)},
            "discard": {"card_index": (int,)},
            "play_card": {"card_index": (int,), "target": (int,)},
            "use_ability": {
                "ability": (str,),
                "indices": (list,),
                "target": (int,),
                "card_index": (int,),
                "discard": (int,),
                "equipment": (int,),
                "card": (int,),
                "use_discard": (bool,),
                "enabled": (bool,),
            },
            "set_auto_miss": {"enabled": (bool,)},
        }

        schema = schemas.get(action)
        if schema is None:
            return False

        for key, value in payload.items():
            if key == "action":
                continue
            expected = schema.get(key)
            if expected is None:
                return False
            if key == "indices":
                if not isinstance(value, list) or not all(isinstance(v, int) for v in value):
                    return False
            elif not isinstance(value, expected):
                return False
        return True

    async def _process_message(self, websocket: ServerConnection, message: str | bytes) -> None:
        """Parse and route a single message from ``websocket``."""

        if message == "end_turn":
            self.game.end_turn()
            await self.broadcast_state()
            return

        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            logger.warning("Malformed JSON from client: %r", message)
            await websocket.send(json.dumps({"error": "invalid json"}))
            return

        if not isinstance(payload, dict):
            logger.warning("Non-object payload received: %r", payload)
            await websocket.send(json.dumps({"error": "invalid message"}))
            return

        if not self._validate_payload(payload):
            logger.warning("Invalid payload received: %r", payload)
            await websocket.send(json.dumps({"error": "invalid message"}))
            return

        action = payload.get("action")
        if action == "draw":
            draw_payload: DrawPayload = cast(DrawPayload, payload)
            await self._handle_draw(websocket, draw_payload)
        elif action == "discard":
            discard_payload: DiscardPayload = cast(DiscardPayload, payload)
            await self._handle_discard(websocket, discard_payload)
        elif action == "play_card":
            play_payload: PlayCardPayload = cast(PlayCardPayload, payload)
            await self._handle_play_card(websocket, play_payload)
        elif action == "use_ability":
            ability_payload: UseAbilityPayload = cast(UseAbilityPayload, payload)
            await self._handle_use_ability(websocket, ability_payload)
        elif action == "set_auto_miss":
            auto_miss_payload: SetAutoMissPayload = cast(SetAutoMissPayload, payload)
            await self._handle_set_auto_miss(websocket, auto_miss_payload)
        else:
            await websocket.send(json.dumps({"error": "invalid message"}))

    async def _handle_draw(self, websocket: ServerConnection, payload: DrawPayload) -> None:
        num = int(payload.get("num", 1))
        player = self.connections[websocket].player
        self.game.draw_card(player, num)
        await self.broadcast_state()

    async def _handle_discard(self, websocket: ServerConnection, payload: DiscardPayload) -> None:
        idx = payload.get("card_index")
        player = self.connections[websocket].player
        if idx is not None and 0 <= idx < len(player.hand):
            card = player.hand[idx]
            self.game.discard_card(player, card)
            await self.broadcast_state()

    async def _handle_play_card(
        self, websocket: ServerConnection, payload: PlayCardPayload
    ) -> None:
        idx = payload.get("card_index")
        target_idx = payload.get("target")
        player = self.connections[websocket].player
        if idx is None or not 0 <= idx < len(player.hand):
            return

        target = None
        if target_idx is not None:
            target = self.game.get_player_by_index(target_idx)
            if target is None:
                return

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
                    message = json.dumps({"prompt": "general_store", "cards": names})
                    self._create_send_task(conn, message)
        else:
            self.game.play_card(player, card, target)
            desc = f"{player.name} played {card.__class__.__name__}"
            if target:
                desc += f" on {target.name}"
            await self.broadcast_state(desc)

    async def _handle_use_ability(
        self, websocket: ServerConnection, payload: UseAbilityPayload
    ) -> None:
        ability = payload.get("ability")
        player = self.connections[websocket].player
        handler = getattr(self, f"_ability_{ability}", None)
        if not handler:
            return
        skip = await handler(player, payload)
        if not skip:
            await self.broadcast_state()

    async def _ability_sid_ketchum(self, player: Player, payload: UseAbilityPayload) -> bool:
        idxs = payload.get("indices") or []
        if player.character and hasattr(player.character, "use_ability"):
            player.character.use_ability(self.game, player, indices=idxs)
        return False

    async def _ability_chuck_wengam(self, player: Player, _payload: UseAbilityPayload) -> bool:
        self.game.chuck_wengam_ability(player)
        return False

    async def _ability_doc_holyday(self, player: Player, payload: UseAbilityPayload) -> bool:
        idxs = payload.get("indices") or []
        self.game.doc_holyday_ability(player, idxs)
        return False

    async def _ability_vera_custer(self, player: Player, payload: UseAbilityPayload) -> bool:
        idx = payload.get("target")
        target = None
        if idx is not None:
            target = self.game.get_player_by_index(idx)
        if target is None:
            return False
        self.game.vera_custer_copy(player, target)
        return False

    async def _ability_jesse_jones(self, player: Player, payload: UseAbilityPayload) -> bool:
        idx = payload.get("target")
        card_idx = payload.get("card_index")
        target = None
        if idx is not None:
            target = self.game.get_player_by_index(idx)
            if target is None:
                return False
        self.game.draw_phase(player, jesse_target=target, jesse_card=card_idx)
        return False

    async def _ability_kit_carlson(self, player: Player, payload: UseAbilityPayload) -> bool:
        discard = payload.get("discard")
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
        return False

    async def _ability_pedro_ramirez(self, player: Player, payload: UseAbilityPayload) -> bool:
        use_discard = bool(payload.get("use_discard", True))
        self.game.draw_phase(player, pedro_use_discard=use_discard)
        return False

    async def _ability_jose_delgado(self, player: Player, payload: UseAbilityPayload) -> bool:
        eq_idx = payload.get("equipment")
        self.game.draw_phase(player, jose_equipment=eq_idx)
        return False

    async def _ability_pat_brennan(self, player: Player, payload: UseAbilityPayload) -> bool:
        idx = payload.get("target")
        card = cast(str | None, payload.get("card"))
        target = None
        if idx is not None:
            target = self.game.get_player_by_index(idx)
            if target is None:
                return False
        self.game.draw_phase(player, pat_target=target, pat_card=card)
        return False

    async def _ability_lucky_duke(self, player: Player, payload: UseAbilityPayload) -> bool:
        idx = payload.get("card_index", 0)
        cards = player.metadata.lucky_cards or []
        player.metadata.lucky_cards = []
        if cards:
            chosen = cards[idx] if idx < len(cards) else cards[0]
            player.hand.append(chosen)
            for c in cards:
                if c is not chosen:
                    self.game.discard_pile.append(c)
            self.game.draw_card(player)
        else:
            self.game.draw_phase(player)
        return False

    async def _ability_uncle_will(self, player: Player, payload: UseAbilityPayload) -> bool:
        cidx = payload.get("card_index")
        if cidx is not None and 0 <= cidx < len(player.hand):
            card = player.hand[cidx]
            if self.game.uncle_will_ability(player, card):
                await self.broadcast_state()
                return True
        return False

    async def _handle_set_auto_miss(
        self, websocket: ServerConnection, payload: SetAutoMissPayload
    ) -> None:
        enabled = bool(payload.get("enabled", True))
        self.connections[websocket].player.metadata.auto_miss = enabled
        await self.broadcast_state()

    async def broadcast_state(self, message: str | None = None) -> None:
        """Send updated game state to all connected clients."""

        async def send_payload(
            websocket: ServerConnection, conn: Connection, payload: dict
        ) -> None:
            try:
                await conn.websocket.send(json.dumps(payload))
            except (OSError, WebSocketException, asyncio.CancelledError) as exc:
                logger.exception("Failed to send state to %s", conn.player.name, exc_info=exc)
                # Remove the player from the game if their websocket is no
                # longer reachable before dropping the connection entirely.
                try:
                    await conn.websocket.close()
                except (OSError, WebSocketException) as close_exc:
                    logger.exception(
                        "Error closing websocket for %s",
                        conn.player.name,
                        exc_info=close_exc,
                    )
                self.game.remove_player(conn.player)
                self.connections.pop(websocket, None)

        async with asyncio.TaskGroup() as tg:
            for websocket, conn in list(self.connections.items()):
                payload = {
                    "players": _serialize_players(self.game.players),
                    "hand": [c.card_name for c in conn.player.hand],
                    "character": getattr(conn.player.character, "name", ""),
                    "event": getattr(self.game.current_event, "name", ""),
                }
                if message:
                    payload["message"] = message
                tg.create_task(send_payload(websocket, conn, payload))

    def _find_connection(self, player: Player) -> Connection | None:
        for conn in self.connections.values():
            if conn.player is player:
                return conn
        return None

    def _on_turn_started(self, player: Player) -> None:
        """Handle start-of-turn prompts for ``player``."""
        conn = self._find_connection(player)
        if not conn:
            return

        from ..characters.vera_custer import VeraCuster

        if isinstance(player.character, VeraCuster):
            self._start_vera_custer(conn, player)
            return

        if player.metadata.awaiting_draw:
            player.metadata.awaiting_draw = False
            self._handle_character_draw_start(conn, player)

    def _start_vera_custer(self, conn: Connection, player: Player) -> None:
        options = [
            {"index": i, "name": p.character.name}
            for i, p in enumerate(self.game.players)
            if p is not player and p.is_alive() and p.character is not None
        ]
        if options:
            payload = json.dumps({"prompt": "vera", "options": options})
            self._create_send_task(conn, payload)

    def _handle_character_draw_start(self, conn: Connection, player: Player) -> None:
        handlers = [
            self._start_jesse_jones,
            self._start_kit_carlson,
            self._start_pedro_ramirez,
            self._start_jose_delgado,
            self._start_pat_brennan,
            self._start_lucky_duke,
        ]
        for handler in handlers:
            if handler(conn, player):
                return
        self.game.draw_phase(player)
        self._spawn_broadcast(self.broadcast_state())

    def _start_jesse_jones(self, conn: Connection, player: Player) -> bool:
        from ..characters.jesse_jones import JesseJones

        if not isinstance(player.character, JesseJones):
            return False
        targets = [
            {"index": i, "name": p.name}
            for i, p in enumerate(self.game.players)
            if p is not player and p.hand
        ]
        if targets:
            payload = json.dumps({"prompt": "jesse_jones", "targets": targets})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player)
            self._spawn_broadcast(self.broadcast_state())
        return True

    def _start_kit_carlson(self, conn: Connection, player: Player) -> bool:
        from ..characters.kit_carlson import KitCarlson

        if not isinstance(player.character, KitCarlson):
            return False
        deck = self.game.deck
        if deck is None:
            return False
        cards = [deck.draw() for _ in range(3)]
        player.metadata.kit_cards = [c for c in cards if c]
        names = [c.card_name for c in player.metadata.kit_cards or []]
        payload = json.dumps({"prompt": "kit_carlson", "cards": names})
        self._create_send_task(conn, payload)
        return True

    def _start_pedro_ramirez(self, conn: Connection, player: Player) -> bool:
        from ..characters.pedro_ramirez import PedroRamirez

        if not isinstance(player.character, PedroRamirez):
            return False
        if self.game.discard_pile:
            payload = json.dumps({"prompt": "pedro_ramirez"})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player, pedro_use_discard=False)
            self._spawn_broadcast(self.broadcast_state())
        return True

    def _start_jose_delgado(self, conn: Connection, player: Player) -> bool:
        from ..characters.jose_delgado import JoseDelgado

        if not isinstance(player.character, JoseDelgado):
            return False
        equips = [
            {"index": i, "name": c.card_name}
            for i, c in enumerate(player.hand)
            if hasattr(c, "slot")
        ]
        if equips:
            payload = json.dumps({"prompt": "jose_delgado", "equipment": equips})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player)
            self._spawn_broadcast(self.broadcast_state())
        return True

    def _start_pat_brennan(self, conn: Connection, player: Player) -> bool:
        from ..characters.pat_brennan import PatBrennan

        if not isinstance(player.character, PatBrennan):
            return False
        targets = []
        for i, p in enumerate(self.game.players):
            if p is player or not p.equipment:
                continue
            targets.append({"index": i, "cards": [c.card_name for c in p.equipment.values()]})
        if targets:
            payload = json.dumps({"prompt": "pat_brennan", "targets": targets})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player)
            self._spawn_broadcast(self.broadcast_state())
        return True

    def _start_lucky_duke(self, conn: Connection, player: Player) -> bool:
        from ..characters.lucky_duke import LuckyDuke

        if not isinstance(player.character, LuckyDuke):
            return False
        deck = self.game.deck
        if deck is None:
            return False
        cards = [deck.draw(), deck.draw()]
        player.metadata.lucky_cards = [c for c in cards if c]
        names = [c.card_name for c in player.metadata.lucky_cards or []]
        if names:
            payload = json.dumps({"prompt": "lucky_duke", "cards": names})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player)
            self._spawn_broadcast(self.broadcast_state())
        return True

    def _on_player_damaged(self, player: Player, _src: Player | None = None) -> None:
        msg = (
            f"{player.name} was eliminated"
            if not player.is_alive()
            else f"{player.name} took damage ({player.health})"
        )
        self._spawn_broadcast(self.broadcast_state(msg))

    def _on_player_healed(self, player: Player) -> None:
        msg = f"{player.name} healed to {player.health}"
        self._spawn_broadcast(self.broadcast_state(msg))

    def _on_game_over(self, result: str) -> None:
        self._spawn_broadcast(self.broadcast_state(result))

    async def start(self) -> None:
        """Start the websocket server and run until cancelled."""
        async with serve(
            self.handler,
            self.host,
            self.port,
            ssl=self.ssl_context,
            max_size=MAX_MESSAGE_SIZE,
        ):
            async with asyncio.TaskGroup() as tg:
                self._broadcast_group = tg
                logger.info(
                    "Server started on %s:%s (code: %s)",
                    self.host,
                    self.port,
                    self.room_code,
                )
                await asyncio.Future()  # run forever
