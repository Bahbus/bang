from __future__ import annotations

import random
from .card import Card
from ..player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_manager import GameManager


class CatBalouCard(Card):
    card_name = "Cat Balou"

    def play(
        self, target: Player, game: GameManager | None = None
    ) -> None:
        if not target:
            return
        if target.hand:
            card = random.choice(target.hand)
            target.hand.remove(card)
            if game:
                game.discard_pile.append(card)
        elif target.equipment:
            card = random.choice(list(target.equipment.values()))
            target.equipment.pop(card.card_name, None)
            if game:
                game.discard_pile.append(card)
