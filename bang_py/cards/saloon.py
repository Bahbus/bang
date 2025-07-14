from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class SaloonCard(BaseCard):
    card_name = "Saloon"
    card_type = "action"
    card_set = "base"
    description = "All players heal 1 health."

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not game:
            return
        for p in game.players:
            before = p.health
            p.heal(1)
            if p.health > before:
                game.on_player_healed(p)
