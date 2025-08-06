"""View top 3 cards; keep 2 and return 1 to the deck. Core set."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class KitCarlson(BaseCharacter):
    name = "Kit Carlson"
    description = (
        "During your draw phase, look at the top three cards of the deck, choose"
        " two to keep and put the other back on top."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(KitCarlson)

        def on_draw(p: "Player", opts: dict) -> bool:
            if p is not player:
                return True
            cards = [gm._draw_from_deck(), gm._draw_from_deck(), gm._draw_from_deck()]
            back_index = opts.get("kit_back")
            if back_index is None or not (0 <= back_index < len(cards)):
                back_index = len(cards) - 1
            for i, c in enumerate(cards):
                if c is None:
                    continue
                if i == back_index:
                    gm.deck.cards.appendleft(c)
                else:
                    player.hand.append(c)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True