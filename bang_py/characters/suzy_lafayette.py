"""Draw a card when you empty your hand. Core set."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class SuzyLafayette(BaseCharacter):
    name = "Suzy Lafayette"
    description = "As soon as you have no cards in hand, draw a card."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(SuzyLafayette)
        player.metadata.draw_when_empty = True
        return True