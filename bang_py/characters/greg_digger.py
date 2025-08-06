"""Gain 2 life when another player dies. Dodge City expansion."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class GregDigger(BaseCharacter):
    name = "Greg Digger"
    description = "Each time a player is eliminated, regain two life points."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(GregDigger)

        def on_death(victim: "Player", _src: "Player | None") -> None:
            if victim is not player and player.is_alive():
                before = player.health
                player.heal(2)
                if player.health > before:
                    gm.on_player_healed(player)

        gm.player_death_listeners.append(on_death)
        return True