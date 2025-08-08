"""Knife card from the Dodge City expansion. Attack at distance 1 that can be dodged."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager

from .bang import BangCard


class KnifeCard(BaseCard):
    """Close range attack that can be dodged like a Bang."""

    card_name = "Knife"
    card_type = "green"
    card_set = "dodge_city"
    description = "Attack at distance 1 that can be dodged."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManager | None = None,
        **kwargs: Any,
    ) -> None:
        if not target or not player:
            return
        if player.distance_to(target) > 1:
            return
        if game and game._auto_miss(target):
            return
        BangCard().play(
            target,
            game=game,
            ignore_equipment=player.metadata.ignore_others_equipment if game else False,
        )
        if game and target.health < target.max_health:
            game.on_player_damaged(target, player)
