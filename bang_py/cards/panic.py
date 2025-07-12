from __future__ import annotations

import random
from .card import Card
from ..player import Player
from typing import TYPE_CHECKING
from ..helpers import handle_out_of_turn_discard

if TYPE_CHECKING:
    from ..game_manager import GameManager


class PanicCard(Card):
    card_name = "Panic!"
    description = "Steal a random card or equipment from another player."

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        if not target or not player:
            return
        if target.hand:
            card = random.choice(target.hand)
            target.hand.remove(card)
            handle_out_of_turn_discard(game, target, card)
            player.hand.append(card)
        elif target.equipment:
            card = random.choice(list(target.equipment.values()))
            target.unequip(card.card_name)
            player.hand.append(card)
