from __future__ import annotations

from .card import Card
from ..player import Player
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


class BeerCard(Card):
    card_name = "Beer"

    def play(self, target: Player) -> None:
        if not target:
            return
        game: Optional["GameManager"] = target.metadata.get("game")
        heal_amt = 1
        if game:
            if game.event_flags.get("no_beer"):
                return
            heal_amt = int(game.event_flags.get("beer_heal", 1))
            alive = [p for p in game.players if p.is_alive()]
            if len(alive) <= 2:
                return
        if target.health < target.max_health:
            target.heal(heal_amt)

