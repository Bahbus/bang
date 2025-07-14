from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class NewIdentityEventCard(BaseEventCard):
    """All players discard their hand and draw the same number of cards."""

    card_name = "New Identity"
    description = "Players redraw hands"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not game:
            return
        for p in game.players:
            num = len(p.hand)
            while p.hand:
                game.discard_pile.append(p.hand.pop())
            if num:
                game.draw_card(p, num)
