from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class PixiePete(BaseCharacter):
    name = "Pixie Pete"
    description = "During your draw phase, draw three cards instead of two."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(PixiePete)

        def on_draw(p: "Player", _opts: dict) -> bool:
            if p is not player:
                return True
            gm.draw_card(player, 3)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
