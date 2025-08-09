"""Can Can card from the Dodge City expansion. Choose a card to discard from any one player."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class CanCanCard(BaseCard):
    """Discard a chosen card from the target."""

    card_name = "Can Can"
    card_type = "green"
    card_set = "dodge_city"
    description = "Choose a card to discard from any one player."

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
        if not target or not game:
            return
        if target.hand and (hand_idx is not None or not target.equipment):
            idx = hand_idx if hand_idx is not None and 0 <= hand_idx < len(target.hand) else 0
            card = target.hand.pop(idx)
            game.discard_pile.append(card)
            handle_out_of_turn_discard(game, target, card)
        elif target.equipment:
            name = equip_name or next(iter(target.equipment))
            equip_card = target.unequip(name)
            if equip_card:
                game.discard_pile.append(equip_card)
