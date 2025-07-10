from __future__ import annotations

from abc import ABC, abstractmethod
from ..player import Player


class Card(ABC):
    card_name: str = "Card"
    suit: str | None
    rank: int | None

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        self.suit = suit
        self.rank = rank

    @abstractmethod
    def play(self, target: Player) -> None:
        """Apply the card effect to the target."""
        raise NotImplementedError
