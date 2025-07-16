from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class JesseJones(BaseCharacter):
    name = "Jesse Jones"
    description = (
        "At the start of your draw phase, you may draw the first card from another "
        "player's hand instead of the deck."
    )
    starting_health = 4


    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(JesseJones)

        def on_draw(p: "Player", opts: dict) -> bool:
            if p is not player:
                return True
            opponents = [t for t in gm.players if t is not player and t.hand]
            if opponents:
                target = opts.get("jesse_target")
                idx = opts.get("jesse_card", 0)
                if target in opponents:
                    if idx is None or idx < 0 or idx >= len(target.hand):
                        idx = 0
                    card = target.hand.pop(idx)
                    player.hand.append(card)
                    gm.draw_card(player)
                else:
                    gm.draw_card(player, 2)
            else:
                gm.draw_card(player, 2)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
