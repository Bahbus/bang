from __future__ import annotations

from abc import ABC, abstractmethod
from ..player import Player


class BaseCard(ABC):
    """Abstract base class for all playing cards."""

    card_name: str = "Card"
    card_type: str = "action"
    card_set: str = "base"
    description: str = ""
    suit: str | None
    rank: int | None

    def __init__(self, suit: str | None = None, rank: int | None = None) -> None:
        self.suit = suit
        self.rank = rank

    @abstractmethod
    def play(self, target: Player | None, **kwargs) -> None:
        """Apply the card effect to the target."""
        raise NotImplementedError
