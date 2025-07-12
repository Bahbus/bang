from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class WhiskyCard(Card):
    """Heal two health points."""

    card_name = "Whisky"
    description = "Heal 2 health."

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not target:
            return
        before = target.health
        target.heal(2)
        if game and target.health > before:
            game.on_player_healed(target)
