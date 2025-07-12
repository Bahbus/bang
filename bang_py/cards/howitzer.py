from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..deck import Deck

from .bang import BangCard


class HowitzerCard(Card):
    """Attack all opponents regardless of distance."""

    card_name = "Howitzer"
    description = "Bang all opponents ignoring distance."
    green_border = True

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
            BangCard().play(p, deck or game.deck)
            if p.health < before:
                game.on_player_damaged(p, player)
