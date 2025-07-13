from __future__ import annotations

from .card import Card
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager import GameManager


class CanCanCard(Card):
    """Discard a chosen card from the target."""

    card_name = "Can Can"
    description = "Choose a card to discard from any one player."
    green_border = True

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        *,
        hand_idx: int | None = None,
        equip_name: str | None = None,
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
            card = target.unequip(name)
            if card:
                game.discard_pile.append(card)
