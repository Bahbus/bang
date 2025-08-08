"""Canteen card from the Dodge City expansion. Heal 1 health."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager import GameManager


class CanteenCard(BaseCard):
    """Refreshment to heal one health."""

    card_name = "Canteen"
    card_type = "green"
    card_set = "dodge_city"
    description = "Heal 1 health."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManager | None = None,
        **kwargs: Any,
    ) -> None:
        if not target:
            return
        before = target.health
        target.heal(1)
        if game and target.health > before:
            game.on_player_healed(target)
