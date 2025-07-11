from __future__ import annotations

from .cards.card import Card
from .player import Player
from .characters import Character, VeraCuster
from typing import Type


def is_heart(card: Card | None) -> bool:
    """Return True if the drawn card is a Heart."""
    return getattr(card, "suit", None) == "Hearts"


def is_spade_between(card: Card | None, low: int, high: int) -> bool:
    """Return True if card is a Spade with rank in [low, high]."""
    if getattr(card, "suit", None) != "Spades":
        return False
    rank = getattr(card, "rank", None)
    return rank is not None and low <= rank <= high


def has_ability(player: Player, char_cls: Type[Character]) -> bool:
    """Return True if the player effectively has the given character ability."""
    if isinstance(player.character, char_cls):
        return True
    if isinstance(player.character, VeraCuster):
        copied = player.metadata.get("vera_copy")
        return bool(copied and issubclass(copied, char_cls))
    return False
