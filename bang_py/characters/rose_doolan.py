"""See all others at distance -1. Core set."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol
    from ..player import Player


class RoseDoolan(BaseCharacter):
    name = "Rose Doolan"
    description = "You see all players at a distance -1."
    range_modifier = 1
    starting_health = 4

    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(RoseDoolan)
        return True
