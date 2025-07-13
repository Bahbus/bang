from __future__ import annotations

import random
from .card import Card
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager import GameManager


class CatBalouCard(Card):
    card_name = "Cat Balou"
    description = (
        "Choose a card from the target's hand or in play and discard it."
    )

    def play(
        self,
        target: Player,
        game: GameManager | None = None,
        *,
        hand_idx: int | None = None,
        equip_name: str | None = None,
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
            card = target.unequip(name)
            if card and game:
                game.discard_pile.append(card)
