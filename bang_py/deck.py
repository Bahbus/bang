from __future__ import annotations

from random import shuffle
from typing import List

from .cards.card import Card


class Deck:
    """Simple deck of cards supporting drawing."""

    def __init__(self, cards: List[Card] | None = None) -> None:
        self.cards: List[Card] = cards[:] if cards else []
        shuffle(self.cards)

    def draw(self) -> Card | None:
        """Draw a card from the deck if available."""
        if self.cards:
            return self.cards.pop()
        return None

    def add(self, card: Card) -> None:
        self.cards.insert(0, card)

    def __len__(self) -> int:
        return len(self.cards)
