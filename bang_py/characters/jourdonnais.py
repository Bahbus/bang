from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class Jourdonnais(BaseCharacter):
    name = "Jourdonnais"
    description = "You are considered to have a Barrel in play at all times."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(Jourdonnais)
        player.metadata.virtual_barrel = True
        return True
