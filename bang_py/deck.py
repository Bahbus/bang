"""Minimal shuffled deck supporting card draws and additions."""

from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterable

from .cards.card import BaseCard


class Deck:
    """Simple deck of cards supporting drawing."""

    def __init__(self, cards: Iterable[BaseCard] | None = None) -> None:
        card_list = list(cards) if cards else []
        random.shuffle(card_list)
        self.cards: deque[BaseCard] = deque(card_list)

    def draw(self) -> BaseCard | None:
        """Draw a card from the deck if available."""
        return self.cards.popleft() if self.cards else None

    def add(self, card: BaseCard) -> None:
        self.cards.append(card)

    def push_top(self, card: BaseCard) -> None:
        """Place a card on top of the deck."""
        self.cards.appendleft(card)

    def extend_top(self, cards: Iterable[BaseCard]) -> None:
        """Place multiple cards on top of the deck.

        The last card from ``cards`` will be drawn first.
        """
        self.cards.extendleft(cards)

    def extend(self, cards: Iterable[BaseCard]) -> None:
        """Append multiple cards to the bottom of the deck."""
        self.cards.extend(cards)

    def shuffle(self) -> None:
        """Shuffle the deck in-place."""
        card_list = list(self.cards)
        random.shuffle(card_list)
        self.cards = deque(card_list)

    def __len__(self) -> int:
        return len(self.cards)
