from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class BangCard(Card):
    card_name = "Bang!"

    def play(self, target: Player, deck: Deck | None = None) -> None:
        if not target:
            return
        if deck:
            barrel = target.equipment.get("Barrel")
            if barrel and getattr(barrel, "draw_check", None):
                if barrel.draw_check(deck):
                    target.metadata["dodged"] = True
                    return
        target.take_damage(1)

