"""Define a minimal shuffled deck supporting card draws and additions."""

from __future__ import annotations

from random import shuffle
from collections import deque

from .cards.card import BaseCard


class Deck:
    """Simple deck of cards supporting drawing."""

    def __init__(self, cards: list[BaseCard] | None = None) -> None:
        card_list = cards[:] if cards else []
        shuffle(card_list)
        self.cards: deque[BaseCard] = deque(card_list)

    def draw(self) -> BaseCard | None:
        """Draw a card from the deck if available."""
        if self.cards:
            return self.cards.popleft()
        return None

    def add(self, card: BaseCard) -> None:
        self.cards.append(card)

    def __len__(self) -> int:
        return len(self.cards)
