from __future__ import annotations

import random
from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager import GameManager


class PanicCard(BaseCard):
    card_name = "Panic!"
    card_type = "action"
    card_set = "base"
    description = (
        "Range 1: choose a card from the target's hand or in play and take it."
    )

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        *,
        hand_idx: int | None = None,
        equip_name: str | None = None,
    ) -> None:
        """Steal a chosen card from the target."""
        if not target or not player:
            return

        if target.hand and (hand_idx is not None or not target.equipment):
            idx = hand_idx if hand_idx is not None and 0 <= hand_idx < len(target.hand) else 0
            card = target.hand.pop(idx)
            handle_out_of_turn_discard(game, target, card)
            player.hand.append(card)
            return

        if target.equipment:
            name = equip_name or next(iter(target.equipment))
            card = target.unequip(name)
            if card:
                player.hand.append(card)
