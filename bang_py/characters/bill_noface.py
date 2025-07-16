from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class BillNoface(BaseCharacter):
    name = "Bill Noface"
    description = (
        "During phase 1 of your turn, draw 1 card plus 1 for each wound you have."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(BillNoface)

        def on_draw(p: "Player", _opts: dict) -> bool:
            if p is not player:
                return True
            wounds = player.max_health - player.health
            gm.draw_card(player, 1 + wounds)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
