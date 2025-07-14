from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class LassoEventCard(BaseEventCard):
    """Each player takes the first card from the next player's hand if possible."""

    card_name = "Lasso"
    description = "Steal from next player"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        players = game.players
        taken: list = []
        for i, p in enumerate(players):
            target_p = players[(i + 1) % len(players)]
            card = target_p.hand.pop(0) if target_p.hand else None
            taken.append(card)
        for card, p in zip(taken, players):
            if card:
                p.hand.append(card)
