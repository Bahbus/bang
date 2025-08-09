"""Draw a card from play instead of the deck. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..player import Player
from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol


class PatBrennan(BaseCharacter):
    name = "Pat Brennan"
    description = (
        "During phase 1 of your turn, you may draw a card in play instead of from the deck."
    )
    starting_health = 4

    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(PatBrennan)

        def on_draw(p: "Player", opts: object) -> bool:
            if p is not player:
                return True
            options: dict[str, object] = opts if isinstance(opts, dict) else {}
            target_obj = options.get("pat_target")
            target_pl = target_obj if isinstance(target_obj, Player) else None
            card_obj = options.get("pat_card")
            card_name = card_obj if isinstance(card_obj, str) else None
            if not gm.pat_brennan_draw(player, target_pl, card_name):
                gm.draw_card(player)
            gm.draw_card(player)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
