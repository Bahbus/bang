from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class PaulRegret(BaseCharacter):
    name = "Paul Regret"
    description = "Players see you at distance +1."
    distance_modifier = 1
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(PaulRegret)
        return True
