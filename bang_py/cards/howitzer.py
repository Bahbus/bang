"""Howitzer card from the Dodge City expansion. Bang all opponents ignoring distance."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager

from .bang import BangCard


class HowitzerCard(BaseCard):
    """Attack all opponents regardless of distance."""

    card_name = "Howitzer"
    card_type = "green"
    card_set = "dodge_city"
    description = "Bang all opponents ignoring distance."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManager | None = None,
        **kwargs: Any,
    ) -> None:
        if not game or not player:
            return
        for p in game.players:
            if p is player:
                continue
            before = p.health
            BangCard().play(
                p,
                game=game,
                ignore_equipment=player.metadata.ignore_others_equipment,
            )
            if p.health < before:
                game.on_player_damaged(p, player)
