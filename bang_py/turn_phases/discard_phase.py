"""Discard phase helpers for :class:`GameManager`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.card import BaseCard

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..player import Player
    from ..game_manager import GameManager


class DiscardPhaseMixin:
    """Provide discard phase logic for :class:`GameManager`."""

    deck: object
    discard_pile: list[BaseCard]
    event_flags: dict

    def discard_phase(self: 'GameManager', player: 'Player') -> None:
        limit = self._hand_limit(player)
        self._discard_to_limit(player, limit)

    def _hand_limit(self, player: 'Player') -> int:
        limit = player.health
        if player.metadata.hand_limit is not None:
            limit = max(limit, player.metadata.hand_limit)
        if player.metadata.no_hand_limit:
            return 99
        if "reverend_limit" in self.event_flags:
            limit = min(limit, int(self.event_flags["reverend_limit"]))
        return limit

    def _discard_to_limit(self, player: 'Player', limit: int) -> None:
        while len(player.hand) > limit:
            card = player.hand.pop()
            if self.event_flags.get("abandoned_mine"):
                self.deck.cards.insert(0, card)
            else:
                self._pass_left_or_discard(player, card)
