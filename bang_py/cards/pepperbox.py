from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..deck import Deck

from .bang import BangCard


class PepperboxCard(BaseCard):
    """Green-bordered Bang! card."""

    card_name = "Pepperbox"
    card_type = "green"
    card_set = "dodge_city"
    description = "Acts as a normal Bang!"

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        deck: Deck | None = None,
    ) -> None:
        if not target or not player:
            return
        if player.distance_to(target) > player.attack_range:
            return
        d = deck or (game.deck if game else None)
        if game and game._auto_miss(target):
            return
        before = target.health
        BangCard().play(target, d)
        if game and target.health < before:
            game.on_player_damaged(target, player)
