"""Play any number of Bang! cards each turn. Core set."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class WillyTheKid(BaseCharacter):
    name = "Willy the Kid"
    description = "You may play any number of Bang! cards during your turn."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(WillyTheKid)
        player.metadata.unlimited_bang = True
        return True