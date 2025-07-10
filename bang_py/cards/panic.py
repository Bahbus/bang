from __future__ import annotations

import random
from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class PanicCard(Card):
    card_name = "Panic!"

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not target or not player:
            return
        if target.hand:
            card = random.choice(target.hand)
            target.hand.remove(card)
            player.hand.append(card)
        elif target.equipment:
            card = random.choice(list(target.equipment.values()))
            target.equipment.pop(card.card_name, None)
            player.hand.append(card)
        if game:
            # No discard since card is stolen
            pass
