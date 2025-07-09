from __future__ import annotations

from abc import ABC, abstractmethod
from ..player import Player


class Card(ABC):
    card_name: str = "Card"

    @abstractmethod
    def play(self, target: Player) -> None:
        """Apply the card effect to the target."""
        raise NotImplementedError
