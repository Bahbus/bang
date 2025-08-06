"""Draw for all, keep two, gift the rest. Bullet expansion exclusive."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class ClausTheSaint(BaseCharacter):
    name = "Claus the Saint"
    description = (
        "During your draw phase, draw one more card than the number of players, "
        "keep two, then give one to each other player."
    )
    starting_health = 3

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(ClausTheSaint)

        def on_draw(p: "Player", _opts: dict) -> bool:
            if p is not player:
                return True
            alive = [pl for pl in gm.players if pl.is_alive()]
            cards = []
            for _ in range(len(alive) + 1):
                card = gm._draw_from_deck()
                if card:
                    cards.append(card)
            keep = cards[:2]
            for c in keep:
                player.hand.append(c)
            others = [pl for pl in alive if pl is not player]
            idx = 2
            for pl in others:
                if idx < len(cards):
                    pl.hand.append(cards[idx])
                    idx += 1
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True