"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List


def _noop(game: "GameManager") -> None:
    """Default no-op event effect."""
    return


def _peyote(game: "GameManager") -> None:
    """Each draw gives one extra card."""
    game.event_flags["peyote_bonus"] = 1


def _ricochet(game: "GameManager") -> None:
    """Bang! cards also hit the next player."""
    game.event_flags["ricochet"] = True


def _river(game: "GameManager") -> None:
    """Discarded cards pass to the left player."""
    game.event_flags["river"] = True


def _fistful_ghost_town(game: "GameManager") -> None:
    """Alias of Ghost Town for the Fistful deck."""
    _ghost_town(game)


def _judge(game: "GameManager") -> None:
    """Beer cards cannot be played."""
    game.event_flags["no_beer_play"] = True


def _ghost_town(game: "GameManager") -> None:
    """Revive eliminated players with 1 health until the next event card."""
    game.event_flags["ghost_town"] = True
    revived = []
    for p in game.players:
        if not p.is_alive():
            p.health = 1
            p.metadata["ghost_revived"] = True
            revived.append(p)
    if revived:
        game.turn_order = [i for i, pl in enumerate(game.players) if pl.is_alive()]


def _bounty(game: "GameManager") -> None:
    """Reward eliminations with two cards."""
    game.event_flags["bounty"] = True


def _vendetta(game: "GameManager") -> None:
    """Outlaws gain +1 attack range."""
    game.event_flags["vendetta"] = True


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
        EventCard(
            "Blessing", lambda g: [p.heal(1) for p in g.players], "All players heal"
        ),
        EventCard(
            "Gold Rush",
            lambda g: g.event_flags.update(draw_count=3),
            "Draw three cards",
        ),
        EventCard("The Judge", _judge, "Beer cards cannot be played"),
        EventCard("Ghost Town", _ghost_town, "Eliminated players return"),
        EventCard(
            "Law of the West",
            lambda g: g.event_flags.update(range_unlimited=True),
            "Unlimited range",
        ),
        EventCard(
            "Siesta", lambda g: g.event_flags.update(draw_count=3), "Draw three cards"
        ),
        EventCard(
            "Cattle Drive",
            lambda g: [p.hand.pop() for p in g.players if p.hand],
            "Discard a card",
        ),
        EventCard(
            "The Sermon",
            lambda g: g.event_flags.update(no_bang=True),
            "Bang! cannot be played",
        ),
        EventCard("Peyote", _peyote, "Lucky draws"),
        EventCard(
            "Hangover",
            lambda g: g.event_flags.update(no_beer=True),
            "Beer gives no health",
        ),
        EventCard("High Noon", _high_noon, "Lose 1 life at start of turn"),
    ]


def create_fistful_deck() -> List[EventCard]:
    """Return a simple Fistful of Cards event deck."""
    return [
        EventCard(
            "Abandoned Mine",
            lambda g: [g.draw_card(p) for p in g.players],
            "Everyone draws",
        ),
        EventCard(
            "Ambush",
            lambda g: g.event_flags.update(no_missed=True),
            "Missed! has no effect",
        ),
        EventCard("Ricochet", _ricochet, "Bang! hits an extra player"),
        EventCard("Ranch", lambda g: [p.heal(1) for p in g.players], "All heal"),
        EventCard(
            "Gold Rush", lambda g: g.event_flags.update(draw_count=3), "Draw extra"
        ),
        EventCard(
            "Hard Liquor", lambda g: g.event_flags.update(beer_heal=2), "Beer heals 2"
        ),
        EventCard("The River", _river, "Discards pass left"),
        EventCard("Bounty", _bounty, "Rewards for eliminations"),
        EventCard("Vendetta", _vendetta, "Outlaws have +1 range"),
        EventCard(
            "Prison Break",
            lambda g: g.event_flags.update(no_jail=True),
            "Jail discarded",
        ),
        EventCard(
            "High Stakes", lambda g: g.event_flags.update(bang_limit=2), "Two Bang!s"
        ),
        EventCard("Ghost Town", _fistful_ghost_town, "Eliminated return"),
        EventCard("A Fistful of Cards", _fistful, "Damage equal to cards in hand"),
    ]
