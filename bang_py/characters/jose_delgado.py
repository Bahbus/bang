"""Discard a blue card to draw two more. Dodge City expansion."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class JoseDelgado(BaseCharacter):
    name = "Jose Delgado"
    description = "You may discard a blue card to draw two cards."
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(JoseDelgado)

        def on_draw(p: "Player", opts: object) -> bool:
            if p is not player:
                return True
            equips = [c for c in player.hand if hasattr(c, "slot")]
            equip = None
            options: dict[str, object] = opts if isinstance(opts, dict) else {}
            sel = options.get("jose_equipment")
            if isinstance(sel, int) and 0 <= sel < len(equips):
                equip = equips[sel]
            elif equips:
                equip = equips[0]
            if equip:
                player.hand.remove(equip)
                gm.discard_pile.append(equip)
                gm.draw_card(player, 2)
            gm.draw_card(player)
            return True

        gm.draw_phase_listeners.append(on_draw)
        return True
