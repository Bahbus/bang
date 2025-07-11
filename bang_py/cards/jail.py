from __future__ import annotations

from .equipment import EquipmentCard
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import is_heart
from ..characters import LuckyDuke

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
        if isinstance(player.character, LuckyDuke):
            card1 = deck.draw()
            card2 = deck.draw()
            result = is_heart(card1) or is_heart(card2)
        else:
            card1 = deck.draw()
            result = is_heart(card1)
        player.unequip(self.card_name)
        return not result
