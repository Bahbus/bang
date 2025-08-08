"""Cat Balou card from the base game.
Choose a card from the target's hand or in play and discard it.
"""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager import GameManager


class CatBalouCard(BaseCard):
    card_name = "Cat Balou"
    card_type = "action"
    card_set = "base"
    description = "Choose a card from the target's hand or in play and discard it."

    @override
    def play(
        self,
        target: Player | None,
        game: GameManager | None = None,
        *,
        hand_idx: int | None = None,
        equip_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Discard a chosen card from the target's hand or equipment."""
        if not target:
            return

        if target.hand and (hand_idx is not None or not target.equipment):
            idx = hand_idx if hand_idx is not None and 0 <= hand_idx < len(target.hand) else 0
            card = target.hand.pop(idx)
            if game:
                game.discard_pile.append(card)
                handle_out_of_turn_discard(game, target, card)
            return

        if target.equipment:
            name = equip_name or next(iter(target.equipment))
            equip_card = target.unequip(name)
            if equip_card and game:
                game.discard_pile.append(equip_card)
