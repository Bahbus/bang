"""Your Bang! requires two Missed! to avoid. Core set."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class SlabTheKiller(BaseCharacter):
    name = "Slab the Killer"
    description = "Players need two Missed! cards to cancel your Bang!."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(SlabTheKiller)
        player.metadata.double_miss = True
        return True