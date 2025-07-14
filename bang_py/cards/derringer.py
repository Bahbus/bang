from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..deck import Deck

from .bang import BangCard


class DerringerCard(BaseCard):
    """Bang at range 1 then draw a card."""

    card_name = "Derringer"
    card_type = "green"
    card_set = "dodge_city"
    description = "Bang at range 1, then draw a card."

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        deck: Deck | None = None,
    ) -> None:
        if not target or not player:
            return
        if player.distance_to(target) > 1:
            return
        d = deck or (game.deck if game else None)
        if game and game._auto_miss(target):
            game.draw_card(player)
            return
        before = target.health
        BangCard().play(target, d)
        if game and target.health < before:
            game.on_player_damaged(target, player)
        if game:
            game.draw_card(player)
