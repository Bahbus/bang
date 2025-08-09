"""Panic! card from the base game. Range 1: choose a card from the target's hand or in play and take
it."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class PanicCard(BaseCard):
    card_name = "Panic!"
    card_type = "action"
    card_set = "base"
    description = "Range 1: choose a card from the target's hand or in play and take it."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        *,
        hand_idx: int | None = None,
        equip_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Steal a chosen card from the target."""
        if not target or not player:
            return

        if target.hand and (hand_idx is not None or not target.equipment):
            idx = hand_idx if hand_idx is not None and 0 <= hand_idx < len(target.hand) else 0
            card = target.hand.pop(idx)
            if game:
                handle_out_of_turn_discard(game, target, card)
            player.hand.append(card)
            return

        if target.equipment:
            name = equip_name or next(iter(target.equipment))
            equip_card = target.unequip(name)
            if equip_card:
                player.hand.append(equip_card)
