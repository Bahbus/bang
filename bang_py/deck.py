"""Define a minimal shuffled deck supporting card draws and additions."""

from __future__ import annotations

from random import shuffle

from .cards.card import BaseCard


class Deck:
    """Simple deck of cards supporting drawing."""

    def __init__(self, cards: list[BaseCard] | None = None) -> None:
        self.cards: list[BaseCard] = cards[:] if cards else []
        shuffle(self.cards)

    def draw(self) -> BaseCard | None:
        """Draw a card from the deck if available."""
        if self.cards:
            return self.cards.pop()
        return None

    def add(self, card: BaseCard) -> None:
        self.cards.insert(0, card)

    def __len__(self) -> int:
        return len(self.cards)
