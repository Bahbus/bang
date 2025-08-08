"""Conestoga card from the Dodge City expansion. Steal a card from any player."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager import GameManager


class ConestogaCard(BaseCard):
    """Steal a card from any one player."""

    card_name = "Conestoga"
    card_type = "green"
    card_set = "dodge_city"
    description = "Steal a card from any player."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManager | None = None,
        *,
        hand_idx: int | None = None,
        equip_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        if not target or not player:
            return
        card: BaseCard | None = None
        if target.hand and (hand_idx is not None or not target.equipment):
            idx = hand_idx if hand_idx is not None and 0 <= hand_idx < len(target.hand) else 0
            card = target.hand.pop(idx)
        elif target.equipment:
            name = equip_name or next(iter(target.equipment))
            card = target.unequip(name)
        if card:
            player.hand.append(card)
