"""Copy another living character's ability each turn. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class VeraCuster(BaseCharacter):
    name = "Vera Custer"
    description = "At the start of your turn, copy another living character's ability."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(VeraCuster)
        return True

    def copy_ability(self, gm: "GameManager", player: "Player", target: "Player") -> bool:
        if not target.is_alive() or target is player or target.character is None:
            return True
        player.metadata.vera_copy = target.character.__class__
        player.metadata.abilities.add(target.character.__class__)
        target.character.ability(gm, player)
        return True
