"""High Noon card from the High Noon expansion. Event: everyone draws one card."""

from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class HighNoonCard(BaseCard):
    """All players draw a card."""

    card_name = "High Noon"
    card_type = "event"
    card_set = "high_noon"
    description = "Event: everyone draws one card."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        for p in game.players:
            game.draw_card(p)
