from __future__ import annotations

from .cards.card import Card


def is_heart(card: Card | None) -> bool:
    """Return True if the drawn card is a Heart."""
    return getattr(card, "suit", None) == "Hearts"


def is_spade_between(card: Card | None, low: int, high: int) -> bool:
    """Return True if card is a Spade with rank in [low, high]."""
    if getattr(card, "suit", None) != "Spades":
        return False
    rank = getattr(card, "rank", None)
    return rank is not None and low <= rank <= high
