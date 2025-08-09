"""Dispatch utilities for card play.

This module contains the core mixin for routing card play actions and
registration of handler groups.
"""

from __future__ import annotations

from importlib import import_module
from collections.abc import Iterable
from typing import TYPE_CHECKING, cast

from ..cards.bang import BangCard
from ..cards.card import BaseCard
from ..cards.jail import JailCard
from ..cards.missed import MissedCard
from ..cards.panic import PanicCard
from ..cards.roles import SheriffRoleCard
from ..event_flags import EventFlags
from ..game_manager_protocol import GameManagerProtocol
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..player import Player

HANDLER_MODULES = {
    "basic": "bang_py.card_handlers.basic",
    "blue": "bang_py.card_handlers.blue",
    "green": "bang_py.card_handlers.green",
    "event": "bang_py.card_handlers.event",
}


def register_handler_groups(game: GameManagerProtocol, groups: Iterable[str]) -> None:
    """Import handler modules for ``groups`` and register them on ``game``."""
    for group in groups:
        module = import_module(HANDLER_MODULES[group])
        module.register(game)


class DispatchMixin:
    """Mixin implementing card play dispatch and general utilities."""

    card_played_listeners: list
    card_play_checks: list
    discard_pile: list
    event_flags: EventFlags
    _card_handlers: dict
    _players: list["Player"]
    turn_order: list[int]
    current_turn: int

    def _handler_self_game(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        card.play(player, game=self)

    def _handler_target_game(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        if target:
            card.play(target, game=self)

    def _handler_target_player_game(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        if target:
            card.play(target, player=player, game=self)

    def _handler_self_player_game(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        card.play(player, player=player, game=self)

    def _handler_target_or_self_player_game(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        card.play(target or player, player=player, game=self)

    def _handler_target_player(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        if target:
            card.play(target, player=player)

    def _register_card_handlers(
        self: GameManagerProtocol, groups: Iterable[str] | None = None
    ) -> None:
        """Populate the card handler registry."""
        self._card_handlers = {}
        register_handler_groups(self, groups or HANDLER_MODULES.keys())

    def _dispatch_play(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        if self._handle_missed_as_bang(player, card, target):
            return
        handler = self._card_handlers.get(type(card))
        if handler:
            handler(player, card, target)
        else:
            card.play(target)

    def _handle_missed_as_bang(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> bool:
        if player.metadata.play_missed_as_bang and isinstance(card, MissedCard) and target:
            handler = self._card_handlers.get(BangCard)
            if handler:
                handler(player, BangCard(), target)
            return True
        return False

    # ------------------------------------------------------------------
    # Card play utilities
    def _pre_card_checks(
        self: GameManagerProtocol, player: "Player", card: BaseCard, target: "Player" | None
    ) -> bool:
        return (
            self._card_in_hand(player, card)
            and self._run_card_play_checks(player, card, target)
            and self._check_target_restrictions(player, card, target)
            and self._check_event_restrictions(player, card)
        )

    def _card_in_hand(self, player: "Player", card: BaseCard) -> bool:
        """Return ``True`` if ``card`` is currently in ``player``'s hand."""
        return card in player.hand

    def _run_card_play_checks(
        self, player: "Player", card: BaseCard, target: "Player" | None
    ) -> bool:
        """Execute registered pre-play checks."""
        for cb in self.card_play_checks:
            if not cb(player, card, target):
                return False
        return True

    def _check_target_restrictions(
        self, player: "Player", card: BaseCard, target: "Player" | None
    ) -> bool:
        """Validate distance and target based limitations."""
        return (
            self._bang_target_valid(player, card, target)
            and self._panic_target_valid(player, card, target)
            and self._jail_target_valid(card, target)
        )

    # ------------------------------------------------------------------
    # Target restriction helpers
    def _bang_target_valid(
        self,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> bool:
        """Check range and sniper restrictions for Bang! cards."""
        if not (isinstance(card, BangCard) and target):
            return True
        if player.distance_to(target) > player.attack_range:
            return False
        if self.event_flags.get("sniper") and player.metadata.use_sniper:
            bang_count = sum(isinstance(c, BangCard) for c in player.hand)
            return bang_count >= 2
        return True

    def _panic_target_valid(
        self, player: "Player", card: BaseCard, target: "Player" | None
    ) -> bool:
        """Panic can only target players within distance 1."""
        if isinstance(card, PanicCard) and target:
            return player.distance_to(target) <= 1
        return True

    def _jail_target_valid(self, card: BaseCard, target: "Player" | None) -> bool:
        """Jail cannot be played on the sheriff."""
        if isinstance(card, JailCard) and target and isinstance(target.role, SheriffRoleCard):
            return False
        return True

    def _check_event_restrictions(self, player: "Player", card: BaseCard) -> bool:
        """Check event related card play restrictions."""
        return not (
            self._jail_blocked(card)
            or self._judge_blocked(card)
            or self._handcuffs_blocked(player, card)
        )

    def _jail_blocked(self, card: BaseCard) -> bool:
        """Return ``True`` if Jail cards are currently banned."""
        return bool(self.event_flags.get("no_jail") and isinstance(card, JailCard))

    def _judge_blocked(self, card: BaseCard) -> bool:
        """Return ``True`` if blue cards are disallowed by The Judge."""
        return bool(self.event_flags.get("judge") and card.card_type in {"blue", "green"})

    def _handcuffs_blocked(self, player: "Player", card: BaseCard) -> bool:
        """Return ``True`` if Handcuffs restricts ``player`` from playing ``card``."""
        if not self.event_flags.get("handcuffs") or not self.event_flags.get("turn_suit"):
            return False
        if not self.turn_order or not self._players:
            return False
        idx = self.turn_order[self.current_turn % len(self.turn_order)]
        if idx >= len(self._players):
            return False
        active = self._players[idx]
        return player is active and getattr(card, "suit", None) != self.event_flags["turn_suit"]

    def _is_bang(
        self: GameManagerProtocol, player: "Player", card: BaseCard, target: "Player" | None
    ) -> bool:
        return bool(
            isinstance(card, BangCard)
            or (player.metadata.play_missed_as_bang and isinstance(card, MissedCard) and target)
        )

    def _can_play_bang(self, player: "Player") -> bool:
        if self.event_flags.get("no_bang"):
            return False
        count = player.metadata.bangs_played
        gun = player.equipment.get("Gun")
        extra = player.metadata.doc_free_bang
        unlimited = (
            player.metadata.unlimited_bang or getattr(gun, "unlimited_bang", False) or extra > 0
        )
        limit = self.event_flags.get("bang_limit", 1)
        return count < limit or unlimited

    def play_card(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None = None,
    ) -> None:
        """Play ``card`` from ``player`` against ``target`` if allowed."""
        if not self._pre_card_checks(player, card, target):
            return

        is_bang = self._is_bang(player, card, target)
        if is_bang and not self._can_play_bang(player):
            return

        player.hand.remove(card)
        before = target.health if target else None
        self._dispatch_play(player, card, target)
        self._notify_card_played(player, card, target)
        self._apply_post_play(player, card, target, before, is_bang)

    def _notify_card_played(
        self: GameManagerProtocol,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
    ) -> None:
        """Call registered card played listeners."""
        for cb in self.card_played_listeners:
            cb(player, card, target)

    def _apply_post_play(
        self,
        player: "Player",
        card: BaseCard,
        target: "Player" | None,
        before: int | None,
        is_bang: bool,
    ) -> None:
        """Handle damage, discard and Bang! bookkeeping."""
        self._apply_damage_and_healing(player, target, before)
        gm = cast(GameManagerProtocol, self)
        gm._pass_left_or_discard(player, card)
        if is_bang:
            gm._update_bang_counters(player)
        gm._draw_if_empty(player)

    def _apply_damage_and_healing(
        self, source: "Player", target: "Player" | None, before: int | None
    ) -> None:
        """Trigger damage or heal callbacks if ``target`` changed health."""
        if target and before is not None:
            gm = cast(GameManagerProtocol, self)
            if target.health < before:
                gm.on_player_damaged(target, source)
            elif target.health > before:
                gm.on_player_healed(target)

    def _draw_if_empty(self: GameManagerProtocol, player: "Player") -> None:
        """Draw a card if the player has an empty hand and may draw."""
        if player.metadata.draw_when_empty and not player.hand:
            self.draw_card(player)

    def _update_bang_counters(self: GameManagerProtocol, player: "Player") -> None:
        """Update Bang! play counters for ``player``."""
        if player.metadata.doc_free_bang > 0:
            player.metadata.doc_free_bang -= 1
        else:
            player.metadata.bangs_played += 1

    def discard_card(self: GameManagerProtocol, player: "Player", card: BaseCard) -> None:
        """Discard ``card`` from ``player`` and process event effects."""
        if card in player.hand:
            player.hand.remove(card)
            gm = cast(GameManagerProtocol, self)
            gm._pass_left_or_discard(player, card)
            if not gm.event_flags.get("river"):
                handle_out_of_turn_discard(gm, player, card)
            if player.metadata.draw_when_empty and not player.hand:
                gm.draw_card(player)

    def _pass_left_or_discard(self: GameManagerProtocol, player: "Player", card: BaseCard) -> None:
        """Pass card to the left during River, otherwise discard."""
        if self.event_flags.get("river"):
            idx = self._players.index(player)
            target = self._players[(idx + 1) % len(self._players)]
            target.hand.append(card)
        else:
            self.discard_pile.append(card)


__all__ = ["DispatchMixin", "register_handler_groups", "HANDLER_MODULES"]
