from __future__ import annotations

from .equipment import EquipmentCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import is_spade_between

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class DynamiteCard(EquipmentCard):
    card_name = "Dynamite"
    description = "Passes around; may explode for 3 damage."

    def play(self, target: Player, deck: Deck | None = None) -> None:
        super().play(target)

    def check_dynamite(
        self, current: Player, next_player: Player, deck: Deck
    ) -> bool:
        """Resolve Dynamite at the start of the current player's turn.

        Returns True if it exploded on the current player.
        """
        card = deck.draw()
        current.equipment.pop(self.card_name, None)
        if is_spade_between(card, 2, 9):
            current.take_damage(3)
            return True
        next_player.equip(self)
        return False
