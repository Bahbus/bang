"""Handlers for Bang! interactions and automatic miss logic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from ..cards.bang import BangCard
from ..cards.missed import MissedCard
from ..cards.card import BaseCard
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class BangHandlersMixin:
    """Mixin providing Bang-specific card resolution helpers."""

    def _play_bang_card(
        self: "GameManager",
        player: "Player",
        card: BangCard,
        target: Optional["Player"],
    ) -> None:
        """Resolve playing a Bang! card with event and equipment modifiers."""
        ignore_eq = player.metadata.ignore_others_equipment
        extra_bang = self._consume_sniper_extra(player, card)
        need_two = player.metadata.double_miss or extra_bang
        if target and need_two:
            if not self._attempt_double_dodge(target):
                card.play(target, self.deck, ignore_equipment=ignore_eq)
        else:
            if not (target and self._auto_miss(target)):
                card.play(target, self.deck, ignore_equipment=ignore_eq)

    def _consume_sniper_extra(
        self: "GameManager", player: "Player", card: BangCard
    ) -> bool:
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

    def _attempt_double_dodge(self: "GameManager", target: "Player") -> bool:
        """Let ``target`` discard two Missed! cards to dodge a Bang!."""
        misses = [c for c in target.hand if isinstance(c, MissedCard)]
        if len(misses) >= 2:
            for _ in range(2):
                mcard = misses.pop()
                target.hand.remove(mcard)
                self.discard_pile.append(mcard)
                handle_out_of_turn_discard(self, target, mcard)
            target.metadata.dodged = True
            return True
        return False

    def _discard_and_record(
        self: "GameManager", player: "Player", card: BaseCard
    ) -> None:
        """Discard ``card`` from ``player`` and note any out-of-turn discard."""
        self._pass_left_or_discard(player, card)
        if not self.event_flags.get("river"):
            handle_out_of_turn_discard(self, player, card)

    def _auto_miss(self: "GameManager", target: "Player") -> bool:
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

    def _should_use_auto_miss(self: "GameManager", target: "Player") -> bool:
        """Return ``True`` if automatic Missed! can be used."""
        if self.event_flags.get("no_missed"):
            return False
        return target.metadata.auto_miss is not False

    def _use_miss_card(self: "GameManager", target: "Player") -> bool:
        """Use a Missed! card from ``target`` if available."""
        miss = next((c for c in target.hand if isinstance(c, MissedCard)), None)
        if miss:
            target.hand.remove(miss)
            self._discard_and_record(target, miss)
            target.metadata.dodged = True
            return True
        return False

    def _use_bang_as_miss(self: "GameManager", target: "Player") -> bool:
        """Use a Bang! card as a Missed! if allowed."""
        if target.metadata.bang_as_missed:
            bang = next((c for c in target.hand if isinstance(c, BangCard)), None)
            if bang:
                target.hand.remove(bang)
                self._discard_and_record(target, bang)
                target.metadata.dodged = True
                return True
        return False

    def _use_any_card_as_miss(self: "GameManager", target: "Player") -> bool:
        """Use any card as a Missed! if permitted by effects."""
        if target.metadata.any_card_as_missed and target.hand:
            card = target.hand.pop()
            self._discard_and_record(target, card)
            target.metadata.dodged = True
            return True
        return False


__all__ = ["BangHandlersMixin"]

