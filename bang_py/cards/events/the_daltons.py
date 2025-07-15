from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheDaltonsEventCard(BaseEventCard):
    """Force each player to discard one equipment if possible."""

    card_name = "The Daltons"
    card_set = "high_noon"
    description = "Discard an equipment"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        for p in game.players:
            if p.equipment:
                name = next(iter(p.equipment))
                card = p.unequip(name)
                if card:
                    game.discard_pile.append(card)
