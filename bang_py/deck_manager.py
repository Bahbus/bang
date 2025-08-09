"""Deck creation and player management utilities."""

from __future__ import annotations

from typing import TYPE_CHECKING
import random

from .cards.card import BaseCard
from .cards.roles import (
    BaseRole,
    DeputyRoleCard,
    OutlawRoleCard,
    RenegadeRoleCard,
    SheriffRoleCard,
)
from .characters.base import BaseCharacter
from .deck import Deck
from .deck_factory import create_standard_deck
from .event_flags import EventFlags
from .game_manager_protocol import GameManagerProtocol

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from .player import Player


class DeckManagerMixin:
    """Handle deck setup and player turn ordering."""

    deck: Deck | None
    expansions: list[str]
    _players: list["Player"]
    discard_pile: list[BaseCard]
    event_flags: EventFlags
    current_turn: int
    turn_order: list[int]

    def _initialize_main_deck(self: GameManagerProtocol) -> None:
        """Create the main deck if needed and ensure event flags exist."""
        if self.deck is None:
            if not self.expansions:
                self.expansions.append("dodge_city")
            self.deck = create_standard_deck(self.expansions)
        self.event_flags = {}

    def add_player(self: GameManagerProtocol, player: "Player") -> None:
        """Add a player to the game and record the game reference."""
        player.metadata.game = self
        self._players.append(player)
        if player.character is not None:
            player.character.ability(self, player)

    def remove_player(self: GameManagerProtocol, player: "Player") -> None:
        """Remove ``player`` from the game and update turn order."""
        if player not in self._players:
            return
        current_obj = self._current_player_obj() if self.turn_order else None
        idx = self._players.index(player)
        self._players.pop(idx)
        player.metadata.game = None
        self._reindex_turn_order(idx)
        if not self.turn_order:
            self.current_turn = 0
            return
        self._reset_current_turn(current_obj)

    def start_game(self: GameManagerProtocol, deal_roles: bool = True) -> None:
        """Begin the game and deal starting hands."""
        if deal_roles:
            self._deal_roles_and_characters()
        self.turn_order = list(range(len(self._players)))
        self.current_turn = 0
        for _ in range(2):
            for player in self._players:
                self.draw_card(player)
        self._begin_turn()

    # ------------------------------------------------------------------
    # Setup helpers
    def _build_role_deck(self: GameManagerProtocol) -> list[type[BaseRole]]:
        """Return role classes for the current player count."""
        role_map = {
            3: [DeputyRoleCard, OutlawRoleCard, RenegadeRoleCard],
            4: [SheriffRoleCard, RenegadeRoleCard, OutlawRoleCard, OutlawRoleCard],
            5: [
                SheriffRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
            6: [
                SheriffRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
            7: [
                SheriffRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
            8: [
                SheriffRoleCard,
                RenegadeRoleCard,
                RenegadeRoleCard,
                DeputyRoleCard,
                DeputyRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
                OutlawRoleCard,
            ],
        }
        classes = role_map.get(len(self._players))
        if not classes:
            raise ValueError("Unsupported player count")
        return list(classes)

    def _build_character_deck(self: GameManagerProtocol) -> list[type[BaseCharacter]]:
        from . import characters

        return [getattr(characters, name) for name in characters.__all__ if name != "BaseCharacter"]

    def choose_character(
        self: GameManagerProtocol, player: "Player", options: list[BaseCharacter]
    ) -> BaseCharacter:
        """Select which character a player will use. Defaults to the first."""
        return options[0]

    def _deal_roles_and_characters(self: GameManagerProtocol) -> None:
        role_classes = self._build_role_deck()
        random.shuffle(role_classes)
        char_deck = [cls() for cls in self._build_character_deck()]
        random.shuffle(char_deck)
        for player in self._players:
            player.role = role_classes.pop()()
            choices = [char_deck.pop(), char_deck.pop()]
            chosen = self.choose_character(player, choices)
            player.character = chosen
            for ch in choices:
                if ch is not chosen:
                    player.metadata.unused_character = ch
                    break
            player.reset_stats()
            player.character.ability(self, player)
            player.metadata.game = self

    def _next_alive_player(self: GameManagerProtocol, player: "Player") -> "Player" | None:
        """Return the next living player to the left."""
        if player not in self._players:
            return None
        idx = self._players.index(player)
        for i in range(1, len(self._players)):
            nxt = self._players[(idx + i) % len(self._players)]
            if nxt.is_alive():
                return nxt
        return None

    def _pass_left_or_discard(self: GameManagerProtocol, source: "Player", card: BaseCard) -> None:
        """Pass card left if The River is active, else discard."""
        if self.event_flags.get("river"):
            target = self._next_alive_player(source)
            if target and target is not source:
                target.hand.append(card)
                return
        self.discard_pile.append(card)

    # ------------------------------------------------------------------
    # Turn management helpers
    def _current_player_obj(self: GameManagerProtocol) -> "Player | None":
        """Return the Player whose turn it currently is or ``None``."""
        if not self.turn_order or not self._players:
            return None
        idx = self.turn_order[self.current_turn % len(self.turn_order)]
        if idx >= len(self._players):
            return None
        return self._players[idx]

    def _reindex_turn_order(self: GameManagerProtocol, removed_idx: int) -> None:
        """Remove ``removed_idx`` from turn order and shift indices."""
        self.turn_order = [
            i - 1 if i > removed_idx else i for i in self.turn_order if i != removed_idx
        ]

    def _reset_current_turn(self: GameManagerProtocol, current_obj: "Player" | None) -> None:
        """Update ``current_turn`` after player removal."""
        if current_obj and current_obj in self._players:
            cur_idx = self._players.index(current_obj)
            if cur_idx in self.turn_order:
                self.current_turn = self.turn_order.index(cur_idx)
                return
        self.current_turn %= len(self.turn_order)

    def _get_player_by_index(self: GameManagerProtocol, idx: int) -> "Player" | None:
        if 0 <= idx < len(self._players):
            return self._players[idx]
        return None

    def get_player_by_index(self: GameManagerProtocol, idx: int) -> "Player" | None:
        """Return the player at ``idx`` if it exists."""
        return self._get_player_by_index(idx)
