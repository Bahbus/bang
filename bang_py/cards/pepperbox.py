"""Pepperbox card from the Dodge City expansion. Acts as a normal Bang! card."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol

from .bang import BangCard


class PepperboxCard(BaseCard):
    """Green-bordered Bang! card."""

    card_name = "Pepperbox"
    card_type = "green"
    card_set = "dodge_city"
    description = "Acts as a normal Bang!"

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        if not target or not player:
            return
        if player.distance_to(target) > player.attack_range:
            return
        if game and game._auto_miss(target):
            return
        before = target.health
        BangCard().play(
            target,
            game=game,
            ignore_equipment=player.metadata.ignore_others_equipment if game else False,
        )
        if game and target.health < before:
            game.on_player_damaged(target, player)
