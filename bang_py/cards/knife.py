from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..deck import Deck

from .bang import BangCard


class KnifeCard(Card):
    """Close range attack that can be dodged like a Bang!"""

    card_name = "Knife"
    description = "Attack at distance 1 that can be dodged."
    green_border = True

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
        BangCard().play(target, deck)
        if game and target.health < target.max_health:
            game.on_player_damaged(target, player)

