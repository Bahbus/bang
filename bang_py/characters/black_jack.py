from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class BlackJack(BaseCharacter):
    name = "Black Jack"
    description = (
        "During your draw phase, reveal the second card. "
        "If it's Heart or Diamond, draw one additional card."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(BlackJack)

        def on_draw(p: "Player", _k: object) -> bool:
            if p is not player:
                return True
            first = gm._draw_from_deck()
            if first:
                player.hand.append(first)
            second = gm._draw_from_deck()
            if second:
                player.hand.append(second)
                if getattr(second, "suit", None) in ("Hearts", "Diamonds"):
                    gm.draw_card(player)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
