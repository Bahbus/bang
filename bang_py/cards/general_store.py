from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class GeneralStoreCard(Card):
    card_name = "General Store"

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not game:
            return
        for p in game.players:
            game.draw_card(p)
