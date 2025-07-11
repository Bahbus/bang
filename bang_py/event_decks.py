"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List

@dataclass
class EventCard:
    """Card used in event deck expansions."""

    name: str
    effect: Callable[["GameManager"], None]
    description: str = ""

    def apply(self, game: "GameManager") -> None:
        """Execute this event's effect."""
        self.effect(game)


def create_high_noon_deck() -> List[EventCard]:
    """Return a simple High Noon event deck."""
    return [EventCard("High Noon", lambda g: None, "No effect")] * 13


def create_fistful_deck() -> List[EventCard]:
    """Return a simple Fistful of Cards event deck."""
    return [EventCard("A Fistful of Cards", lambda g: None, "No effect")] * 13

