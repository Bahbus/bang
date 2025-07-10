from __future__ import annotations

from .equipment import EquipmentCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import is_heart

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..deck import Deck


class JailCard(EquipmentCard):
    card_name = "Jail"
    description = "Skip your turn unless you draw a Heart."

    def play(self, target: Player, deck: Deck | None = None) -> None:
        super().play(target)

    def check_turn(self, player: Player, deck: Deck) -> bool:
        """Handle start-of-turn Jail check.

        Returns True if the player's turn is skipped.
        """
        card = deck.draw()
        player.equipment.pop(self.card_name, None)
        return not is_heart(card)
