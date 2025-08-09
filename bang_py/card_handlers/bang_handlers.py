"""Handlers for Bang! interactions and automatic miss logic."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.bang import BangCard
from ..cards.missed import MissedCard
from ..cards.card import BaseCard
from ..game_manager_protocol import GameManagerProtocol
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..player import Player


class BangHandlersMixin:
    """Mixin providing Bang-specific card resolution helpers."""

    def _play_bang_card(
        self: GameManagerProtocol,
        player: "Player",
        card: BangCard,
        target: "Player" | None,
    ) -> None:
        """Resolve playing a Bang! card with event and equipment modifiers."""
        ignore_eq = player.metadata.ignore_others_equipment
        extra_bang = self._consume_sniper_extra(player, card)
        need_two = player.metadata.double_miss or extra_bang
        if target and need_two:
            if not self._attempt_double_dodge(target):
                card.play(target, game=self, ignore_equipment=ignore_eq)
        else:
            if not (target and self._auto_miss(target)):
                card.play(target, game=self, ignore_equipment=ignore_eq)

    def _consume_sniper_extra(self: GameManagerProtocol, player: "Player", card: BangCard) -> bool:
        """Discard an extra Bang! when Sniper event is active and return True if consumed."""
        if self.event_flags.get("sniper") and player.metadata.use_sniper:
            extra = next(
                (c for c in player.hand if isinstance(c, BangCard) and c is not card),
                None,
            )
            player.metadata.use_sniper = False
            if extra:
                player.hand.remove(extra)
                self._pass_left_or_discard(player, extra)
                return True
        return False

    def _attempt_double_dodge(self: GameManagerProtocol, player: "Player") -> bool:
        """Let ``player`` discard two Missed! cards to dodge a Bang!."""
        misses = [c for c in player.hand if isinstance(c, MissedCard)]
        if len(misses) >= 2:
            for _ in range(2):
                mcard = misses.pop()
                player.hand.remove(mcard)
                self.discard_pile.append(mcard)
                handle_out_of_turn_discard(self, player, mcard)
            player.metadata.dodged = True
            return True
        return False

    def _discard_and_record(self: GameManagerProtocol, player: "Player", card: BaseCard) -> None:
        """Discard ``card`` from ``player`` and note any out-of-turn discard."""
        self._pass_left_or_discard(player, card)
        if not self.event_flags.get("river"):
            handle_out_of_turn_discard(self, player, card)

    def _auto_miss(self: GameManagerProtocol, target: "Player") -> bool:
        """Attempt to satisfy a Bang! with automatic Missed! effects."""
        if not self._should_use_auto_miss(target):
            return False
        if self._use_miss_card(target):
            return True
        if self._use_bang_as_miss(target):
            return True
        if self._use_any_card_as_miss(target):
            return True
        return False

    def _should_use_auto_miss(self: GameManagerProtocol, target: "Player") -> bool:
        """Return ``True`` if automatic Missed! can be used."""
        if self.event_flags.get("no_missed"):
            return False
        return target.metadata.auto_miss is not False

    def _use_miss_card(self: GameManagerProtocol, player: "Player") -> bool:
        """Use a Missed! card from ``player`` if available."""
        miss = next((c for c in player.hand if isinstance(c, MissedCard)), None)
        if miss:
            player.hand.remove(miss)
            self._discard_and_record(player, miss)
            player.metadata.dodged = True
            return True
        return False

    def _use_bang_as_miss(self: GameManagerProtocol, player: "Player") -> bool:
        """Use a Bang! card as a Missed! if allowed."""
        if player.metadata.bang_as_missed:
            bang = next((c for c in player.hand if isinstance(c, BangCard)), None)
            if bang:
                player.hand.remove(bang)
                self._discard_and_record(player, bang)
                player.metadata.dodged = True
                return True
        return False

    def _use_any_card_as_miss(self: GameManagerProtocol, player: "Player") -> bool:
        """Use any card as a Missed! if permitted by effects."""
        if player.metadata.any_card_as_missed and player.hand:
            card = player.hand.pop()
            self._discard_and_record(player, card)
            player.metadata.dodged = True
            return True
        return False


__all__ = ["BangHandlersMixin"]
