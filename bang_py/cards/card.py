"""Base class and metadata for all Bang! playing cards."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..player import Player


class BaseCard(ABC):
    """Abstract base class for all playing cards."""

    # These metadata fields are accessed by the deck builder and UI via
    # ``getattr``. They remain here even if not referenced within this module
    # so Vulture may flag them as unused.
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
        # ``**kwargs`` allows subclasses to accept extra parameters without
        # changing the base class signature.
        raise NotImplementedError
