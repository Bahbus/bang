from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class CalamityJanet(BaseCharacter):
    name = "Calamity Janet"
    description = "You may play Bang! cards as Missed! and vice versa."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(CalamityJanet)
        player.metadata.play_missed_as_bang = True
        player.metadata.bang_as_missed = True
        return True
