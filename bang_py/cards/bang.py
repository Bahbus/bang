from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import is_heart
from ..characters import Jourdonnais, LuckyDuke
from .barrel import BarrelCard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class BangCard(BaseCard):
    card_name = "Bang!"
    card_type = "action"
    card_set = "base"
    description = "Basic attack that deals 1 damage unless dodged."

    def play(
        self,
        target: Player,
        deck: Deck | None = None,
        *,
        ignore_equipment: bool = False,
    ) -> None:
        if not target:
            return
        if deck and not ignore_equipment:
            barrel = target.equipment.get("Barrel")
            if barrel and getattr(barrel, "draw_check", None):
                if barrel.draw_check(deck, target):
                    target.metadata.dodged = True
                    return
            if isinstance(target.character, Jourdonnais):
                if BarrelCard().draw_check(deck, target):
                    target.metadata.dodged = True
                    return
            if isinstance(target.character, LuckyDuke):
                card1 = deck.draw()
                card2 = deck.draw()
                if is_heart(card1) or is_heart(card2):
                    target.metadata.dodged = True
                    return
        target.take_damage(1)
