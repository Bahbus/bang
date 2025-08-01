from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager

from .bang import BangCard


class KnifeCard(BaseCard):
    """Close range attack that can be dodged like a Bang."""

    card_name = "Knife"
    card_type = "green"
    card_set = "dodge_city"
    description = "Attack at distance 1 that can be dodged."

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not target or not player:
            return
        if player.distance_to(target) > 1:
            return
        deck = game.deck if game else None
        if game and game._auto_miss(target):
            return
        BangCard().play(
            target,
            deck,
            ignore_equipment=player.metadata.ignore_others_equipment if game else False,
        )
        if game and target.health < target.max_health:
            game.on_player_damaged(target, player)
