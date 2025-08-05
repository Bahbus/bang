"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import TYPE_CHECKING

from .cards.events import (
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
from .player import Player

if TYPE_CHECKING:
    from .game_manager import GameManager


def _peyote(game: GameManager) -> None:
    PeyoteEventCard().play(game=game)


def _ricochet(game: GameManager) -> None:
    RicochetEventCard().play(game=game)


def _judge(game: GameManager) -> None:
    TheJudgeEventCard().play(game=game)


def _ghost_town(game: GameManager) -> None:
    GhostTownEventCard().play(game=game)


def _vendetta(game: GameManager) -> None:
    VendettaEventCard().play(game=game)


def _thirst(game: GameManager) -> None:
    ThirstEventCard().play(game=game)


def _shootout(game: GameManager) -> None:
    ShootoutEventCard().play(game=game)


def _high_noon(game: GameManager) -> None:
    HighNoonEventCard().play(game=game)


def _fistful(game: GameManager) -> None:
    FistfulOfCardsEventCard().play(game=game)


def _blessing(game: GameManager) -> None:
    BlessingEventCard().play(game=game)


def _gold_rush(game: GameManager) -> None:
    GoldRushEventCard().play(game=game)


def _law_of_the_west(game: GameManager) -> None:
    LawOfTheWestEventCard().play(game=game)


def _sermon(game: GameManager) -> None:
    TheSermonEventCard().play(game=game)


def _hangover(game: GameManager) -> None:
    HangoverEventCard().play(game=game)


def _abandoned_mine(game: GameManager) -> None:
    AbandonedMineEventCard().play(game=game)


def _ambush_event(game: GameManager) -> None:
    AmbushEventCard().play(game=game)


def _ranch(game: GameManager) -> None:
    RanchEventCard().play(game=game)


def _hard_liquor(game: GameManager) -> None:
    HardLiquorEventCard().play(game=game)


def _blood_brothers(game: GameManager) -> None:
    BloodBrothersEventCard().play(game=game)


def _daltons_event(game: GameManager) -> None:
    TheDaltonsEventCard().play(game=game)


def _doctor_event(game: GameManager) -> None:
    TheDoctorEventCard().play(game=game)


def _reverend_event(game: GameManager) -> None:
    TheReverendEventCard().play(game=game)


def _train_arrival_event(game: GameManager) -> None:
    TrainArrivalEventCard().play(game=game)


def _handcuffs_event(game: GameManager) -> None:
    HandcuffsEventCard().play(game=game)


def _new_identity_event(game: GameManager) -> None:
    NewIdentityEventCard().play(game=game)


def _lasso_event(game: GameManager) -> None:
    LassoEventCard().play(game=game)


def _sniper_event(game: GameManager) -> None:
    SniperEventCard().play(game=game)


def _russian_roulette_event(game: GameManager) -> None:
    RussianRouletteEventCard().play(game=game)


@dataclass
class EventCard:
    """Card used in event deck expansions."""

    name: str
    effect: Callable[[GameManager], None]
    description: str = ""

    card_type: str = "event"
    card_set: str = "event_deck"
    suit: str | None = None
    rank: int | None = None

    def __post_init__(self) -> None:
        """Set ``card_name`` to the event name."""
        self.card_name = self.name

    def apply(self, game: GameManager) -> None:
        """Execute this event's effect."""
        self.effect(game)

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:  # pragma: no cover - simple passthrough
        """Play this event card if a game is provided."""
        if game:
            self.apply(game)


def create_high_noon_deck() -> list[BaseEventCard]:
    """Return a simple High Noon event deck."""
    return [
        BlessingEventCard(),
        CurseEventCard(),
        GhostTownEventCard(),
        GoldRushEventCard(),
        HangoverEventCard(),
        HighNoonEventCard(),
        ShootoutEventCard(),
        TheDaltonsEventCard(),
        TheDoctorEventCard(),
        TheReverendEventCard(),
        TheSermonEventCard(),
        ThirstEventCard(),
        TrainArrivalEventCard(),
        HandcuffsEventCard(),
        NewIdentityEventCard(),
    ]


def create_fistful_deck() -> list[BaseEventCard]:
    """Return a simple Fistful of Cards event deck."""
    return [
        AbandonedMineEventCard(),
        AmbushEventCard(),
        BloodBrothersEventCard(),
        DeadManEventCard(),
        HardLiquorEventCard(),
        LassoEventCard(),
        LawOfTheWestEventCard(),
        PeyoteEventCard(),
        RanchEventCard(),
        RicochetEventCard(),
        RussianRouletteEventCard(),
        SniperEventCard(),
        TheJudgeEventCard(),
        VendettaEventCard(),
        FistfulOfCardsEventCard(),
    ]
