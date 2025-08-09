"""Beer heals you by 2 instead of 1. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol
    from ..player import Player


class TequilaJoe(BaseCharacter):
    name = "Tequila Joe"
    description = "Beer cards heal you by 2 life points."
    starting_health = 4

    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(TequilaJoe)
        player.metadata.beer_heal_bonus = 1
        return True
