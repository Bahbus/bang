from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class CanteenCard(BaseCard):
    """Refreshment to heal one health."""

    card_name = "Canteen"
    card_type = "green"
    card_set = "dodge_city"
    description = "Heal 1 health."

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if not target:
            return
        before = target.health
        target.heal(1)
        if game and target.health > before:
            game.on_player_healed(target)
