from __future__ import annotations

from .card import Card
from ..player import Player
import random
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..game_manager import GameManager


class GeneralStoreCard(Card):
    card_name = "General Store"

    def play(
        self, target: Player, player: Player | None = None, game: GameManager | None = None
    ) -> None:
        """Draw ``len(players)`` cards and allow each player to select one."""
        if not game or not player:
            return

        alive = [p for p in game.players if p.is_alive()]
        cards: List[Card] = []
        for _ in range(len(alive)):
            card = game.deck.draw()
            if card is None:
                if game.discard_pile:
                    game.deck.cards.extend(game.discard_pile)
                    game.discard_pile.clear()
                    random.shuffle(game.deck.cards)
                    card = game.deck.draw()
            if card:
                cards.append(card)

        start_idx = game.players.index(player)
        for i in range(len(alive)):
            p = game.players[(start_idx + i) % len(game.players)]
            if p.is_alive() and cards:
                chosen = cards.pop(0)
                p.hand.append(chosen)

        for leftover in cards:
            game.discard_pile.append(leftover)
