"""Steal a card instead of drawing the first. Core set."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..player import Player
from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


class JesseJones(BaseCharacter):
    name = "Jesse Jones"
    description = (
        "At the start of your draw phase, you may draw the first card from another "
        "player's hand instead of the deck."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(JesseJones)

        def on_draw(p: "Player", opts: object) -> bool:
            if p is not player:
                return True
            opponents = [t for t in gm.players if t is not player and t.hand]
            if opponents:
                options: dict[str, object] = opts if isinstance(opts, dict) else {}
                target_obj = options.get("jesse_target")
                target_pl = target_obj if isinstance(target_obj, Player) else None
                idx_obj = options.get("jesse_card", 0)
                idx = idx_obj if isinstance(idx_obj, int) else 0
                if target_pl in opponents:
                    if idx < 0 or idx >= len(target_pl.hand):
                        idx = 0
                    card = target_pl.hand.pop(idx)
                    player.hand.append(card)
                    gm.draw_card(player)
                else:
                    gm.draw_card(player, 2)
            else:
                gm.draw_card(player, 2)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
