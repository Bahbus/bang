"""Gatling card from the base game. Bang every other player once."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager import GameManager


class GatlingCard(BaseCard):
    card_name = "Gatling"
    card_type = "action"
    card_set = "base"
    description = "Bang every other player once."

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
            from .bang import BangCard

            BangCard().play(
                p,
                game=game,
                ignore_equipment=player.metadata.ignore_others_equipment,
            )
            if p.health < before:
                game.on_player_damaged(p, player)
