"""Bang! card from the base game. Basic attack that deals 1 damage unless dodged."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from .barrel import BarrelCard
from ..characters.jourdonnais import Jourdonnais

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck
    from ..game_manager_protocol import GameManagerProtocol


class BangCard(BaseCard):
    card_name = "Bang!"
    card_type = "action"
    card_set = "base"
    description = "Basic attack that deals 1 damage unless dodged."

    @override
    def play(
        self,
        target: Player | None,
        deck: Deck | None = None,
        *,
        game: "GameManagerProtocol" | None = None,
        ignore_equipment: bool = False,
        **kwargs: Any,
    ) -> None:
        if not target:
            return
        gm = game or target.metadata.game if target else None
        if gm and not ignore_equipment:
            barrel = target.equipment.get("Barrel")
            if isinstance(barrel, BarrelCard) and barrel.draw_check(gm, target):
                target.metadata.dodged = True
                return
            if isinstance(target.character, Jourdonnais) or target.metadata.virtual_barrel:
                if BarrelCard().draw_check(gm, target):
                    target.metadata.dodged = True
                    return
        target.take_damage(1)
