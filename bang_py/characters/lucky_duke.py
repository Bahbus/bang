"""Draw! twice and choose the result you prefer. Core set."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class LuckyDuke(BaseCharacter):
    name = "Lucky Duke"
    description = (
        "Whenever you must draw! you flip two cards and choose the result you prefer."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(LuckyDuke)
        player.metadata.lucky_duke = True
        return True