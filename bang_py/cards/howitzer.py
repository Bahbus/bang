"""Howitzer card from the Dodge City expansion. Bang all opponents ignoring distance."""

from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..deck import Deck

from .bang import BangCard


class HowitzerCard(BaseCard):
    """Attack all opponents regardless of distance."""

    card_name = "Howitzer"
    card_type = "green"
    card_set = "dodge_city"
    description = "Bang all opponents ignoring distance."

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None,
        deck: Deck | None = None
    ) -> None:
        if not game or not player:
            return
        for p in game.players:
            if p is player:
                continue
            before = p.health
            BangCard().play(
                p,
                deck or game.deck,
                ignore_equipment=player.metadata.ignore_others_equipment,
            )
            if p.health < before:
                game.on_player_damaged(p, player)
