from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player

class PedroRamirez(BaseCharacter):
    name = "Pedro Ramirez"
    description = (
        "At the start of your draw phase, you may take the top card from the discard "
        "pile instead of drawing."
    )
    starting_health = 4


    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(PedroRamirez)
        def on_draw(p: "Player", opts: dict) -> bool:
            if p is not player or not gm.discard_pile:
                return True
            use_discard = opts.get("pedro_use_discard", True)
            if use_discard:
                player.hand.append(gm.discard_pile.pop())
                gm.draw_card(player)
            else:
                gm.draw_card(player, 2)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
