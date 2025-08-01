from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class SeanMallory(BaseCharacter):
    name = "Sean Mallory"
    description = "You may hold up to 10 cards in your hand."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(SeanMallory)
        player.metadata.hand_limit = 10
        return True
