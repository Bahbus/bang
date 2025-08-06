"""Websocket server implementation for hosting a Bang game."""

import asyncio
import json
import os
import secrets
import ssl
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any
import logging

from cryptography.fernet import Fernet

from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import WebSocketException

from ..game_manager import GameManager
from ..player import Player
from ..characters.jesse_jones import JesseJones
from ..characters.jose_delgado import JoseDelgado
from ..characters.kit_carlson import KitCarlson
from ..characters.lucky_duke import LuckyDuke
from ..characters.pat_brennan import PatBrennan
from ..characters.pedro_ramirez import PedroRamirez
from ..characters.vera_custer import VeraCuster
from ..cards.general_store import GeneralStoreCard

logger = logging.getLogger(__name__)

# Maximum allowed size for incoming websocket messages
MAX_MESSAGE_SIZE = 4096

# Default key for join tokens used in tests and examples.
DEFAULT_TOKEN_KEY = b"xPv7Sx0hWCLo5A9HhF_zvg87gdRSB8OYBjWM7lV-H2I="

ENV_TOKEN_KEY = "BANG_TOKEN_KEY"


def _token_key_bytes(key: bytes | str | None) -> bytes:
    """Return ``key`` as bytes or read it from ``BANG_TOKEN_KEY``.

    Raises:
        ValueError: if no key is provided and the environment variable is unset.
    """

    if key is None:
        env = os.getenv(ENV_TOKEN_KEY)
        if env is None:
            raise ValueError(
                "Token key not provided and BANG_TOKEN_KEY environment variable is missing"
            )
        key = env
    return key if isinstance(key, bytes) else key.encode()


def generate_join_token(
    host: str, port: int, code: str, key: bytes | str | None = None
) -> str:
    """Return an encrypted token identifying a game room."""

    key_bytes = _token_key_bytes(key)
    data = json.dumps({"host": host, "port": port, "code": code}).encode()
    return Fernet(key_bytes).encrypt(data).decode()


def parse_join_token(
    token: str, key: bytes | str | None = None
) -> tuple[str, int, str]:
    """Decode ``token`` and return ``(host, port, code)``."""

    key_bytes = _token_key_bytes(key)
    data = Fernet(key_bytes).decrypt(token.encode())
    obj = json.loads(data.decode())
    return obj["host"], int(obj["port"]), obj["code"]


@dataclass
class Connection:
    websocket: ServerConnection
    player: Player
    tasks: set[asyncio.Task] = field(default_factory=set)


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


def validate_player_name(name: str) -> bool:
    """Return ``True`` if ``name`` is a valid player name."""

    if not isinstance(name, str):
        return False
    name = name.strip()
    return bool(name) and len(name) <= 20 and name.isprintable()


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
        self.game = GameManager(expansions=expansions or [])
        self.token_key = _token_key_bytes(token_key)
        self.connections: dict[ServerConnection, Connection] = {}
        self.max_players = max_players
        self.certfile = certfile
        self.keyfile = keyfile
        self.ssl_context: ssl.SSLContext | None = None
        if certfile:
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_context.load_cert_chain(certfile, keyfile)
        self.game.player_damaged_listeners.append(self._on_player_damaged)
        self.game.player_healed_listeners.append(self._on_player_healed)
        self.game.game_over_listeners.append(self._on_game_over)
        self.game.turn_started_listeners.append(self._on_turn_started)

    def generate_join_token(self) -> str:
        """Return an encoded join token for this server."""

        return generate_join_token(
            self.host, self.port, self.room_code, self.token_key
        )

    def parse_join_token(self, token: str) -> tuple[str, int, str]:
        """Decode ``token`` using the server's join token key."""

        return parse_join_token(token, self.token_key)

    def _create_send_task(self, conn: Connection, payload: str) -> None:
        """Create a task to send ``payload`` and track its lifecycle."""

        async def _send() -> None:
            try:
                await conn.websocket.send(payload)
            except asyncio.CancelledError as exc:  # pragma: no cover - network
                logger.warning("Send to %s cancelled", conn.player.name, exc_info=exc)
                raise
            except WebSocketException as exc:  # pragma: no cover - network
                logger.exception("Send to %s failed", conn.player.name, exc_info=exc)

        task = asyncio.create_task(_send())
        conn.tasks.add(task)

        def _remove(t: asyncio.Task) -> None:
            conn.tasks.discard(t)

        task.add_done_callback(_remove)

    async def handler(self, websocket: ServerConnection) -> None:
        """Register a new client and process game commands sent over the socket."""
        await websocket.send("Enter room code:")
        code = await websocket.recv()
        if code != self.room_code:
            await websocket.send("Invalid room code")
            return

        await websocket.send("Enter your name:")
        name = await websocket.recv()
        if not validate_player_name(name):
            await websocket.send("Invalid name")
            return
        name = name.strip()
        if len(self.game.players) >= self.max_players:
            await websocket.send("Game full")
            return

        player = Player(name)
        player.metadata.auto_miss = True
        self.game.add_player(player)
        self.connections[websocket] = Connection(websocket, player)
        await websocket.send(f"Joined game as {player.name}")
        await self.broadcast_state()

        try:
            async for message in websocket:
                if len(message) > MAX_MESSAGE_SIZE:
                    await websocket.close(code=1009, reason="Message too large")
                    break
                await self._process_message(websocket, message)
        finally:
            self.game.remove_player(player)
            conn = self.connections.pop(websocket, None)
            if conn:
                for task in list(conn.tasks):
                    task.cancel()
                if conn.tasks:
                    await asyncio.gather(*conn.tasks, return_exceptions=True)
            await self.broadcast_state()

    def _validate_payload(self, data: dict[str, Any]) -> bool:
        """Validate that ``data`` conforms to the expected schema."""
        action = data.get("action")
        if not isinstance(action, str):
            return False

        schemas: dict[str, dict[str, tuple[type, ...]]] = {
            "draw": {"num": (int,)},
            "discard": {"card_index": (int,)},
            "play_card": {"card_index": (int,), "target": (int,)},
            "general_store_pick": {"index": (int,)},
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

        for key, value in data.items():
            if key == "action":
                continue
            expected = schema.get(key)
            if expected is None:
                return False
            if key == "indices":
                if not isinstance(value, list) or not all(
                    isinstance(v, int) for v in value
                ):
                    return False
            elif not isinstance(value, expected):
                return False
        return True

    async def _process_message(
        self, websocket: ServerConnection, message: str | bytes
    ) -> None:
        """Parse and route a single message from ``websocket``."""
        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            data = message

        if data == "end_turn":
            self.game.end_turn()
            await self.broadcast_state()
            return

        if not isinstance(data, dict):
            return

        if not self._validate_payload(data):
            await websocket.send(json.dumps({"error": "invalid message"}))
            return

        action = data.get("action")
        if action == "draw":
            await self._handle_draw(websocket, data)
        elif action == "discard":
            await self._handle_discard(websocket, data)
        elif action == "play_card":
            await self._handle_play_card(websocket, data)
        elif action == "general_store_pick":
            await self._handle_general_store_pick(websocket, data)
        elif action == "use_ability":
            await self._handle_use_ability(websocket, data)
        elif action == "set_auto_miss":
            await self._handle_set_auto_miss(websocket, data)

    async def _handle_draw(
        self, websocket: ServerConnection, data: dict[str, Any]
    ) -> None:
        num = int(data.get("num", 1))
        player = self.connections[websocket].player
        self.game.draw_card(player, num)
        await self.broadcast_state()

    async def _handle_discard(
        self, websocket: ServerConnection, data: dict[str, Any]
    ) -> None:
        idx = data.get("card_index")
        player = self.connections[websocket].player
        if idx is not None and 0 <= idx < len(player.hand):
            card = player.hand[idx]
            self.game.discard_card(player, card)
            await self.broadcast_state()

    async def _handle_play_card(
        self, websocket: ServerConnection, data: dict[str, Any]
    ) -> None:
        idx = data.get("card_index")
        target_idx = data.get("target")
        player = self.connections[websocket].player
        if idx is None or not 0 <= idx < len(player.hand):
            return

        target = None
        if target_idx is not None:
            target = self.game.get_player_by_index(target_idx)

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
                    payload = json.dumps({"prompt": "general_store", "cards": names})
                    self._create_send_task(conn, payload)
        else:
            self.game.play_card(player, card, target)
            desc = f"{player.name} played {card.__class__.__name__}"
            if target:
                desc += f" on {target.name}"
            await self.broadcast_state(desc)

    async def _handle_general_store_pick(
        self, websocket: ServerConnection, data: dict[str, Any]
    ) -> None:
        idx = data.get("index")
        player = self.connections[websocket].player
        if not isinstance(idx, int) or self.game.general_store_cards is None:
            return

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
                                c.card_name for c in self.game.general_store_cards
                            ],
                        }
                    )
                    self._create_send_task(conn, payload)

    async def _handle_use_ability(
        self, websocket: ServerConnection, data: dict[str, Any]
    ) -> None:
        ability = data.get("ability")
        player = self.connections[websocket].player
        handler = getattr(self, f"_ability_{ability}", None)
        if not handler:
            return
        skip = await handler(player, data)
        if not skip:
            await self.broadcast_state()

    async def _ability_sid_ketchum(self, player: Player, data: dict[str, Any]) -> bool:
        idxs = data.get("indices") or []
        self.game.sid_ketchum_ability(player, idxs)
        return False

    async def _ability_chuck_wengam(
        self, player: Player, _data: dict[str, Any]
    ) -> bool:
        self.game.chuck_wengam_ability(player)
        return False

    async def _ability_doc_holyday(self, player: Player, data: dict[str, Any]) -> bool:
        idxs = data.get("indices") or []
        self.game.doc_holyday_ability(player, idxs)
        return False

    async def _ability_vera_custer(self, player: Player, data: dict[str, Any]) -> bool:
        idx = data.get("target")
        target = self.game.get_player_by_index(idx) if idx is not None else None
        if target:
            self.game.vera_custer_copy(player, target)
        return False

    async def _ability_jesse_jones(self, player: Player, data: dict[str, Any]) -> bool:
        idx = data.get("target")
        card_idx = data.get("card_index")
        target = self.game.get_player_by_index(idx) if idx is not None else None
        self.game.draw_phase(player, jesse_target=target, jesse_card=card_idx)
        return False

    async def _ability_kit_carlson(self, player: Player, data: dict[str, Any]) -> bool:
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
        return False

    async def _ability_pedro_ramirez(
        self, player: Player, data: dict[str, Any]
    ) -> bool:
        use_discard = bool(data.get("use_discard", True))
        self.game.draw_phase(player, pedro_use_discard=use_discard)
        return False

    async def _ability_jose_delgado(self, player: Player, data: dict[str, Any]) -> bool:
        eq_idx = data.get("equipment")
        self.game.draw_phase(player, jose_equipment=eq_idx)
        return False

    async def _ability_pat_brennan(self, player: Player, data: dict[str, Any]) -> bool:
        idx = data.get("target")
        card = data.get("card")
        target = self.game.get_player_by_index(idx) if idx is not None else None
        self.game.draw_phase(player, pat_target=target, pat_card=card)
        return False

    async def _ability_lucky_duke(self, player: Player, data: dict[str, Any]) -> bool:
        idx = data.get("card_index", 0)
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

    async def _ability_uncle_will(self, player: Player, data: dict[str, Any]) -> bool:
        cidx = data.get("card_index")
        if cidx is not None and 0 <= cidx < len(player.hand):
            card = player.hand[cidx]
            if self.game.uncle_will_ability(player, card):
                await self.broadcast_state()
                return True
        return False

    async def _handle_set_auto_miss(
        self, websocket: ServerConnection, data: dict[str, Any]
    ) -> None:
        enabled = bool(data.get("enabled", True))
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
                logger.exception(
                    "Failed to send state to %s", conn.player.name, exc_info=exc
                )
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

        tasks = []
        for websocket, conn in list(self.connections.items()):
            payload = {
                "players": _serialize_players(self.game.players),
                "hand": [c.card_name for c in conn.player.hand],
                "character": getattr(conn.player.character, "name", ""),
                "event": getattr(self.game.current_event, "name", ""),
            }
            if message:
                payload["message"] = message
            tasks.append(send_payload(websocket, conn, payload))

        if tasks:
            await asyncio.gather(*tasks)

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
            if p is not player and p.is_alive()
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
        asyncio.create_task(self.broadcast_state())

    def _start_jesse_jones(self, conn: Connection, player: Player) -> bool:
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
            asyncio.create_task(self.broadcast_state())
        return True

    def _start_kit_carlson(self, conn: Connection, player: Player) -> bool:
        if not isinstance(player.character, KitCarlson):
            return False
        cards = [self.game.deck.draw() for _ in range(3)]
        player.metadata.kit_cards = [c for c in cards if c]
        names = [c.card_name for c in player.metadata.kit_cards or []]
        payload = json.dumps({"prompt": "kit_carlson", "cards": names})
        self._create_send_task(conn, payload)
        return True

    def _start_pedro_ramirez(self, conn: Connection, player: Player) -> bool:
        if not isinstance(player.character, PedroRamirez):
            return False
        if self.game.discard_pile:
            payload = json.dumps({"prompt": "pedro_ramirez"})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player, pedro_use_discard=False)
            asyncio.create_task(self.broadcast_state())
        return True

    def _start_jose_delgado(self, conn: Connection, player: Player) -> bool:
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
            asyncio.create_task(self.broadcast_state())
        return True

    def _start_pat_brennan(self, conn: Connection, player: Player) -> bool:
        if not isinstance(player.character, PatBrennan):
            return False
        targets = []
        for i, p in enumerate(self.game.players):
            if p is player or not p.equipment:
                continue
            targets.append(
                {"index": i, "cards": [c.card_name for c in p.equipment.values()]}
            )
        if targets:
            payload = json.dumps({"prompt": "pat_brennan", "targets": targets})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player)
            asyncio.create_task(self.broadcast_state())
        return True

    def _start_lucky_duke(self, conn: Connection, player: Player) -> bool:
        if not isinstance(player.character, LuckyDuke):
            return False
        cards = [self.game.deck.draw(), self.game.deck.draw()]
        player.metadata.lucky_cards = [c for c in cards if c]
        names = [c.card_name for c in player.metadata.lucky_cards or []]
        if names:
            payload = json.dumps({"prompt": "lucky_duke", "cards": names})
            self._create_send_task(conn, payload)
        else:
            self.game.draw_phase(player)
            asyncio.create_task(self.broadcast_state())
        return True

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
        async with serve(
            self.handler,
            self.host,
            self.port,
            ssl=self.ssl_context,
            max_size=MAX_MESSAGE_SIZE,
        ):
            logger.info(
                "Server started on %s:%s (code: %s)",
                self.host,
                self.port,
                self.room_code,
            )
            await asyncio.Future()  # run forever


def main() -> None:
    """Entry point for the ``bang-server`` console script."""
    import argparse

    parser = argparse.ArgumentParser(description="Start Bang websocket server")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--certfile", help="Path to SSL certificate", default=None)
    parser.add_argument("--keyfile", help="Path to SSL key", default=None)
    parser.add_argument("--token-key", help="Key for join tokens", default=None)
    parser.add_argument(
        "--show-token", action="store_true", help="Display join token and exit"
    )
    args = parser.parse_args()

    server = BangServer(
        host=args.host,
        port=args.port,
        certfile=args.certfile,
        keyfile=args.keyfile,
        token_key=args.token_key,
    )

    if args.show_token:
        print(server.generate_join_token())
        return

    asyncio.run(server.start())


if __name__ == "__main__":
    main()
