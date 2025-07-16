from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class PatBrennan(BaseCharacter):
    name = "Pat Brennan"
    description = (
        "During phase 1 of your turn, you may draw a card in play instead of from the deck."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(PatBrennan)

        def on_draw(p: "Player", opts: dict) -> bool:
            if p is not player:
                return True
            target = opts.get("pat_target")
            card_name = opts.get("pat_card")
            if not gm.pat_brennan_draw(player, target, card_name):
                gm.draw_card(player)
            gm.draw_card(player)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
