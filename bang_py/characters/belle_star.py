"""Ignore other players' equipment on your turn. Dodge City expansion."""
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseCharacter

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class BelleStar(BaseCharacter):
    name = "Belle Star"
    description = (
        "During your turn, cards in play in front of other players have no effect."
    )
    starting_health = 4

    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        player.metadata.abilities.add(BelleStar)

        def _toggle(p: "Player") -> None:
            player.metadata.ignore_others_equipment = p is player

        gm.turn_started_listeners.append(_toggle)
        return True