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
        if game:
            alive = [p for p in game.players if p.is_alive()]
            if len(alive) <= 2:
                return
        if target.health < target.max_health:
            target.heal(1)

