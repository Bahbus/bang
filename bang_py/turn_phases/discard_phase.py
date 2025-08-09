"""Discard phase helpers for :class:`GameManager`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.card import BaseCard
from ..event_flags import EventFlags
from ..game_manager_protocol import GameManagerProtocol

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..player import Player


class DiscardPhaseMixin:
    """Provide discard phase logic for :class:`GameManager`."""

    deck: Deck | None
    discard_pile: list[BaseCard]
    event_flags: EventFlags

    def discard_phase(self: GameManagerProtocol, player: "Player") -> None:
        limit = self._hand_limit(player)
        self._discard_to_limit(player, limit)

    def _hand_limit(self: GameManagerProtocol, player: "Player") -> int:
        limit = player.health
        if player.metadata.hand_limit is not None:
            limit = max(limit, player.metadata.hand_limit)
        if player.metadata.no_hand_limit:
            return 99
        if "reverend_limit" in self.event_flags:
            limit = min(limit, self.event_flags["reverend_limit"])
        return limit

    def _discard_to_limit(self: GameManagerProtocol, player: "Player", limit: int) -> None:
        while len(player.hand) > limit:
            card = player.hand.pop()
            if self.event_flags.get("abandoned_mine"):
                deck = self.deck
                if deck is None:
                    raise RuntimeError("Deck required")
                deck.push_top(card)
            else:
                self._pass_left_or_discard(player, card)
