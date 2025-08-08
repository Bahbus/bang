"""Buffalo Rifle card from the Dodge City expansion. Bang any player regardless of distance."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager

from .bang import BangCard


class BuffaloRifleCard(BaseCard):
    """Bang any player regardless of distance."""

    card_name = "Buffalo Rifle"
    card_type = "green"
    card_set = "dodge_city"
    description = "Bang any player regardless of distance."

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
        if game and game._auto_miss(target):
            return
        before = target.health
        BangCard().play(
            target,
            game=game,
            ignore_equipment=player.metadata.ignore_others_equipment if player else False,
        )
        if game and player and target.health < before:
            game.on_player_damaged(target, player)
