"""Event deck related utilities for GameManager."""

from __future__ import annotations

from typing import TYPE_CHECKING
import random
from collections import deque

from .event_decks import EventCard, create_high_noon_deck, create_fistful_deck
from ..cards.roles import SheriffRoleCard
from ..player import Player

if TYPE_CHECKING:
    from ..game_manager import GameManager


class EventLogicMixin:
    """Mixin providing event deck helpers for :class:`GameManager`."""

    event_deck: deque[EventCard] | None
    current_event: EventCard | None
    event_flags: dict
    expansions: list[str]
    deck: object
    discard_pile: list[object]
    _players: list[object]
    turn_order: list[int]
    current_turn: int
    first_eliminated: object | None

    def draw_event_card(self: "GameManager") -> None:
        """Draw and apply the next event card."""
        if not self.event_deck:
            return
        self.current_event = self.event_deck.popleft()
        self.event_flags.clear()
        self.current_event.apply(self)

    def _initialize_event_deck(self: "GameManager") -> None:
        """Build and shuffle the event deck based on active expansions."""
        if "high_noon" in self.expansions:
            self.event_deck = self._prepare_high_noon_deck()
        elif "fistful_of_cards" in self.expansions:
            self.event_deck = self._prepare_fistful_deck()
        elif self.event_deck:
            deck_list = list(self.event_deck)
            random.shuffle(deck_list)
            self.event_deck = deque(deck_list)

    def _prepare_high_noon_deck(self: "GameManager") -> deque[EventCard] | None:
        """Create and shuffle the High Noon event deck."""
        deck = create_high_noon_deck()
        if deck:
            deck_list = list(deck)
            final = next((c for c in deck_list if c.name == "High Noon"), None)
            if final:
                deck_list.remove(final)
                random.shuffle(deck_list)
                deck_list.append(final)
            deck = deque(deck_list)
        return deck

    def _prepare_fistful_deck(self: "GameManager") -> deque[EventCard] | None:
        """Create and shuffle the Fistful of Cards event deck."""
        deck = create_fistful_deck()
        if deck:
            deck_list = list(deck)
            final = next((c for c in deck_list if c.name == "A Fistful of Cards"), None)
            if final:
                deck_list.remove(final)
                random.shuffle(deck_list)
                deck_list.append(final)
            deck = deque(deck_list)
        return deck

    def _apply_event_start_effects(self: "GameManager", player: Player) -> Player | None:
        """Run start-of-turn event logic."""
        pre_ghost = self.event_flags.get("ghost_town")
        player = self._sheriff_event_updates(player, bool(pre_ghost))

        self._process_new_identity(player)

        if self._skip_turn_if_needed():
            return None

        if not self._apply_start_damage(player):
            return None

        if not self._apply_fistful_of_cards(player):
            return None

        self._handle_dead_man(player)

        return player

    def _sheriff_event_updates(self: "GameManager", player, pre_ghost: bool):
        """Update sheriff counters and remove Ghost Town revivals."""
        if isinstance(player.role, SheriffRoleCard):
            self._increment_sheriff_turns()
            if pre_ghost and self.event_deck and self.sheriff_turns >= 2:
                player = self._ghost_town_cleanup(player)
        return player

    def _increment_sheriff_turns(self: "GameManager") -> None:
        """Increment sheriff turn count and draw events when eligible."""
        self.sheriff_turns += 1
        if self.event_deck and self.sheriff_turns >= 2:
            self.draw_event_card()

    def _ghost_town_cleanup(self: "GameManager", player):
        """Remove revived ghosts after two sheriff turns."""
        removed = False
        for pl in self._players:
            if pl.metadata.ghost_revived and pl.is_alive():
                pl.health = 0
                pl.metadata.ghost_revived = False
                removed = True
        if removed:
            self.turn_order = [i for i, pl in enumerate(self._players) if pl.is_alive()]
            if player in self._players and self.turn_order:
                player_idx = self._players.index(player)
                if player_idx in self.turn_order:
                    self.current_turn = self.turn_order.index(player_idx)
                    idx = self.turn_order[self.current_turn]
                    if idx < len(self._players):
                        player = self._players[idx]
        return player

    def _process_new_identity(self: "GameManager", player) -> None:
        if self.event_flags.get("new_identity") and player.metadata.unused_character:
            if self.prompt_new_identity(player):
                self.apply_new_identity(player)

    def apply_new_identity(self: "GameManager", player: Player) -> None:
        """Swap ``player`` to their unused character if the event is active."""

        if not self.event_flags.get("new_identity"):
            return
        new_char = player.metadata.unused_character
        if not new_char:
            return
        old_char = player.character
        player.character = new_char
        player.metadata.unused_character = old_char
        player.reset_stats()
        player.character.ability(self, player)
        player.health = min(2, player.max_health)

    def _skip_turn_if_needed(self: "GameManager") -> bool:
        if self.event_flags.get("skip_turn"):
            self.event_flags.pop("skip_turn")
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
            self._begin_turn()
            return True
        return False

    def _apply_start_damage(self: "GameManager", player) -> bool:
        dmg = self.event_flags.get("start_damage", 0)
        if dmg:
            player.take_damage(dmg)
            self.on_player_damaged(player)
            if not player.is_alive():
                self._begin_turn()
                return False
        return True

    def _apply_fistful_of_cards(self: "GameManager", player) -> bool:
        if self.event_flags.get("fistful_of_cards"):
            for _ in range(len(player.hand)):
                if not self._auto_miss(player):
                    player.take_damage(1)
                    self.on_player_damaged(player)
                    if not player.is_alive():
                        self._begin_turn()
                        return False
        return True

    def _handle_dead_man(self: "GameManager", player) -> None:
        if (
            self.event_flags.get("dead_man")
            and self.event_flags.get("dead_man_player") is player
            and not player.is_alive()
            and not self.event_flags.get("dead_man_used")
        ):
            player.health = 2
            self.draw_card(player, 2)
            self.event_flags["dead_man_used"] = True

    def _maybe_revive_ghost_town(self: "GameManager", player) -> bool:
        if self.event_flags.get("ghost_town") and not player.is_alive():
            player.health = 1
            player.metadata.ghost_revived = True
            self.draw_card(player, 3)
            player.metadata.bangs_played = 0
            for cb in self.turn_started_listeners:
                cb(player)
            return True
        return False

    def _handle_vendetta(self: "GameManager", player) -> bool:
        if not self.event_flags.get("vendetta") or player in self.event_flags.get(
            "vendetta_used", set()
        ):
            return False
        card = self._draw_from_deck()
        if card:
            self.discard_pile.append(card)
            if card.suit == "Hearts":
                self.event_flags.setdefault("vendetta_used", set()).add(player)
                self._begin_turn()
                return True
        return False

    def _finish_ghost_town(self: "GameManager", player) -> None:
        if self.event_flags.get("ghost_town") and player.metadata.ghost_revived:
            player.health = 0
            player.metadata.ghost_revived = False
            self._check_win_conditions()
