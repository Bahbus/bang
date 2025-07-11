"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List


def _noop(game: "GameManager") -> None:
    """Default no-op event effect."""
    return


def _thirst(game: "GameManager") -> None:
    game.event_flags["draw_count"] = 1


def _shootout(game: "GameManager") -> None:
    game.event_flags["bang_limit"] = 2


def _high_noon(game: "GameManager") -> None:
    game.event_flags["start_damage"] = 1


def _fistful(game: "GameManager") -> None:
    game.event_flags["damage_by_hand"] = True

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
    return [
        EventCard("Thirst", _thirst, "Players draw only one card"),
        EventCard("Shootout", _shootout, "Play two Bang!s per turn"),
        EventCard("Blessing", lambda g: [p.heal(1) for p in g.players], "All players heal"),
        EventCard("Gold Rush", lambda g: g.event_flags.update(draw_count=3), "Draw three cards"),
        EventCard("The Judge", _noop, "Beer has no effect"),
        EventCard("Ghost Town", _noop, "Eliminated players return for one turn"),
        EventCard("Law of the West", lambda g: g.event_flags.update(range_unlimited=True), "Unlimited range"),
        EventCard("Siesta", lambda g: g.event_flags.update(draw_count=3), "Draw three cards"),
        EventCard("Cattle Drive", lambda g: [p.hand.pop() for p in g.players if p.hand], "Discard a card"),
        EventCard("The Sermon", lambda g: g.event_flags.update(no_bang=True), "Bang! cannot be played"),
        EventCard("Peyote", _noop, "Lucky draws"),
        EventCard("Hangover", lambda g: g.event_flags.update(no_beer=True), "Beer gives no health"),
        EventCard("High Noon", _high_noon, "Lose 1 life at start of turn"),
    ]


def create_fistful_deck() -> List[EventCard]:
    """Return a simple Fistful of Cards event deck."""
    return [
        EventCard("Abandoned Mine", lambda g: [g.draw_card(p) for p in g.players], "Everyone draws"),
        EventCard("Ambush", lambda g: g.event_flags.update(no_missed=True), "Missed! has no effect"),
        EventCard("Ricochet", _noop, "Bang! hits an extra player"),
        EventCard("Ranch", lambda g: [p.heal(1) for p in g.players], "All heal"),
        EventCard("Gold Rush", lambda g: g.event_flags.update(draw_count=3), "Draw extra"),
        EventCard("Hard Liquor", lambda g: g.event_flags.update(beer_heal=2), "Beer heals 2"),
        EventCard("The River", _noop, "Discards pass left"),
        EventCard("Bounty", _noop, "Rewards for eliminations"),
        EventCard("Vendetta", _noop, "Outlaws have +1 range"),
        EventCard("Prison Break", lambda g: g.event_flags.update(no_jail=True), "Jail discarded"),
        EventCard("High Stakes", lambda g: g.event_flags.update(bang_limit=2), "Two Bang!s"),
        EventCard("Ghost Town", _noop, "Eliminated return"),
        EventCard("A Fistful of Cards", _fistful, "Damage equal to cards in hand"),
    ]

