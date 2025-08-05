"""The Daltons card from the High Noon expansion. When The Daltons enters play, each player that has
any blue cards in front of them must choose one to discard."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheDaltonsEventCard(BaseEventCard):
    """Players with blue cards must discard one when this enters play."""

    card_name = "The Daltons"
    card_set = "high_noon"
    description = (
        "When The Daltons enters play, each player that has any blue "
        "cards in front of them must choose one to discard."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the The Daltons event."""
        if not game:
            return
        for p in game.players:
            if p.equipment:
                name = next(iter(p.equipment))
                card = p.unequip(name)
                if card:
                    game.discard_pile.append(card)
