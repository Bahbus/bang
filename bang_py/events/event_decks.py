"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from collections.abc import Callable
from typing import TYPE_CHECKING

from ..cards.events import (
    BaseEventCard,
    AbandonedMineEventCard,
    AmbushEventCard,
    BloodBrothersEventCard,
    DeadManEventCard,
    HardLiquorEventCard,
    LassoEventCard,
    LawOfTheWestEventCard,
    PeyoteEventCard,
    RanchEventCard,
    RicochetEventCard,
    RussianRouletteEventCard,
    SniperEventCard,
    TheJudgeEventCard,
    VendettaEventCard,
    FistfulOfCardsEventCard,
    BlessingEventCard,
    CurseEventCard,
    GhostTownEventCard,
    GoldRushEventCard,
    HangoverEventCard,
    HighNoonEventCard,
    ShootoutEventCard,
    TheDaltonsEventCard,
    TheDoctorEventCard,
    TheReverendEventCard,
    TheSermonEventCard,
    ThirstEventCard,
    TrainArrivalEventCard,
    HandcuffsEventCard,
    NewIdentityEventCard,
)
from ..player import Player

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..game_manager_protocol import GameManagerProtocol


EVENT_CARD_MAP: dict[str, type[BaseEventCard]] = {
    "Abandoned Mine": AbandonedMineEventCard,
    "Ambush": AmbushEventCard,
    "A Fistful of Cards": FistfulOfCardsEventCard,
    "Blessing": BlessingEventCard,
    "Blood Brothers": BloodBrothersEventCard,
    "Curse": CurseEventCard,
    "Dead Man": DeadManEventCard,
    "Ghost Town": GhostTownEventCard,
    "Gold Rush": GoldRushEventCard,
    "Hangover": HangoverEventCard,
    "Hard Liquor": HardLiquorEventCard,
    "Handcuffs": HandcuffsEventCard,
    "High Noon": HighNoonEventCard,
    "Law of the West": LawOfTheWestEventCard,
    "Lasso": LassoEventCard,
    "New Identity": NewIdentityEventCard,
    "Peyote": PeyoteEventCard,
    "Ranch": RanchEventCard,
    "Ricochet": RicochetEventCard,
    "Russian Roulette": RussianRouletteEventCard,
    "Shootout": ShootoutEventCard,
    "Sniper": SniperEventCard,
    "The Daltons": TheDaltonsEventCard,
    "The Doctor": TheDoctorEventCard,
    "The Judge": TheJudgeEventCard,
    "The Reverend": TheReverendEventCard,
    "The Sermon": TheSermonEventCard,
    "Thirst": ThirstEventCard,
    "Train Arrival": TrainArrivalEventCard,
    "Vendetta": VendettaEventCard,
}


@dataclass(slots=True)
class EventCard:
    """Card used in event deck expansions."""

    name: str
    effect: Callable[[GameManagerProtocol], None]
    description: str = ""

    card_type: str = "event"
    card_set: str = "event_deck"
    suit: str | None = None
    rank: int | None = None
    card_name: str = field(init=False)

    def __post_init__(self) -> None:
        """Set ``card_name`` to the event name."""
        self.card_name = self.name

    def apply(self, game: GameManagerProtocol) -> None:
        """Execute this event's effect."""
        self.effect(game)

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:  # pragma: no cover - simple passthrough
        """Play this event card if a game is provided."""
        if game:
            self.apply(game)


def create_high_noon_deck() -> deque[BaseEventCard]:
    """Return a simple High Noon event deck."""
    names = [
        "Blessing",
        "Curse",
        "Ghost Town",
        "Gold Rush",
        "Hangover",
        "High Noon",
        "Shootout",
        "The Daltons",
        "The Doctor",
        "The Reverend",
        "The Sermon",
        "Thirst",
        "Train Arrival",
        "Handcuffs",
        "New Identity",
    ]
    return deque(EVENT_CARD_MAP[n]() for n in names)


def create_fistful_deck() -> deque[BaseEventCard]:
    """Return a simple Fistful of Cards event deck."""
    names = [
        "Abandoned Mine",
        "Ambush",
        "Blood Brothers",
        "Dead Man",
        "Hard Liquor",
        "Lasso",
        "Law of the West",
        "Peyote",
        "Ranch",
        "Ricochet",
        "Russian Roulette",
        "Sniper",
        "The Judge",
        "Vendetta",
        "A Fistful of Cards",
    ]
    return deque(EVENT_CARD_MAP[n]() for n in names)
