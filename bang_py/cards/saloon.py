"""Saloon card from the base game. All players heal 1 health."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager import GameManager


class SaloonCard(BaseCard):
    card_name = "Saloon"
    card_type = "action"
    card_set = "base"
    description = "All players heal 1 health."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManager | None = None,
        **kwargs: Any,
    ) -> None:
        if not game:
            return
        for p in game.players:
            before = p.health
            p.heal(1)
            if p.health > before:
                game.on_player_healed(p)
