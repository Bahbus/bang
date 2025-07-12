from __future__ import annotations

from .card import Card
from ..player import Player


class PunchCard(Card):
    """Simple attack card from the Dodge City expansion."""

    card_name = "Punch"
    description = "Deal 1 damage if the target is within distance 1."

    def play(self, target: Player, player: Player | None = None) -> None:
        """Deal one damage if the target is within distance 1."""
        if not target or not player:
            return
        if player.distance_to(target) > 1:
            return
        before = target.health
        target.take_damage(1)
        if target.health < before and target.metadata.game:
            target.metadata.game.on_player_damaged(target, player)
