"""Simple event deck implementations for optional expansions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, TYPE_CHECKING

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
    BountyEventCard,
    SiestaEventCard,
    RiverEventCard,
    CattleDriveEventCard,
    PrisonBreakEventCard,
    HighStakesEventCard,
)
from .player import Player

if TYPE_CHECKING:
    from .game_manager import GameManager


def _peyote(game: GameManager) -> None:
    """Each draw gives one extra card."""
    PeyoteEventCard().play(game=game)


def _ricochet(game: GameManager) -> None:
    """Bang! cards also hit the next player."""
    RicochetEventCard().play(game=game)


def _river(game: GameManager) -> None:
    """Discarded cards pass to the left player."""
    RiverEventCard().play(game=game)




def _judge(game: GameManager) -> None:
    """Beer cards cannot be played."""
    TheJudgeEventCard().play(game=game)


def _ghost_town(game: GameManager) -> None:
    """Revive eliminated players with 1 health until the next event card."""
    GhostTownEventCard().play(game=game)


def _bounty(game: GameManager) -> None:
    """Reward eliminations with two cards."""
    BountyEventCard().play(game=game)


def _vendetta(game: GameManager) -> None:
    """Outlaws gain +1 attack range."""
    VendettaEventCard().play(game=game)


def _thirst(game: GameManager) -> None:
    ThirstEventCard().play(game=game)


def _shootout(game: GameManager) -> None:
    """Allow unlimited Bang! cards this turn."""
    ShootoutEventCard().play(game=game)


def _high_noon(game: GameManager) -> None:
    HighNoonEventCard().play(game=game)


def _fistful(game: GameManager) -> None:
    FistfulOfCardsEventCard().play(game=game)


def _blessing(game: GameManager) -> None:
    """Heal all players by one."""
    BlessingEventCard().play(game=game)


def _gold_rush(game: GameManager) -> None:
    """Players draw three cards each draw phase."""
    GoldRushEventCard().play(game=game)


def _law_of_the_west(game: GameManager) -> None:
    """Second drawn card must be revealed and played if possible."""
    LawOfTheWestEventCard().play(game=game)


def _siesta(game: GameManager) -> None:
    """Players draw three cards each draw phase."""
    SiestaEventCard().play(game=game)


def _cattle_drive(game: GameManager) -> None:
    """Each player discards one card if possible."""
    CattleDriveEventCard().play(game=game)


def _sermon(game: GameManager) -> None:
    """Bang! cards cannot be played."""
    TheSermonEventCard().play(game=game)


def _hangover(game: GameManager) -> None:
    """Beer cards give no health."""
    HangoverEventCard().play(game=game)


def _abandoned_mine(game: GameManager) -> None:
    """Draw from discard pile and discard to the deck top."""
    AbandonedMineEventCard().play(game=game)


def _ambush_event(game: GameManager) -> None:
    """Treat all players as distance 1 apart."""
    AmbushEventCard().play(game=game)


def _ranch(game: GameManager) -> None:
    """Allow a one-time discard and redraw after the draw phase."""
    RanchEventCard().play(game=game)


def _hard_liquor(game: GameManager) -> None:
    """Players may skip drawing to heal 1 life."""
    HardLiquorEventCard().play(game=game)


def _prison_break(game: GameManager) -> None:
    """Jail cards are discarded."""
    PrisonBreakEventCard().play(game=game)




def _daltons_event(game: GameManager) -> None:
    """Each player draws a card."""
    TheDaltonsEventCard().play(game=game)


def _doctor_event(game: GameManager) -> None:
    """Players heal 1 life instead of drawing cards."""
    TheDoctorEventCard().play(game=game)


def _reverend_event(game: GameManager) -> None:
    """Limit each player to two cards per turn."""
    TheReverendEventCard().play(game=game)


def _train_arrival_event(game: GameManager) -> None:
    """All players draw one card."""
    TrainArrivalEventCard().play(game=game)


def _handcuffs_event(game: GameManager) -> None:
    """Skip the next player's turn."""
    HandcuffsEventCard().play(game=game)


def _new_identity_event(game: GameManager) -> None:
    """All players discard their hand and draw the same number of cards."""
    NewIdentityEventCard().play(game=game)


def _lasso_event(game: GameManager) -> None:
    """Each player takes the first card from the next player's hand if possible."""
    LassoEventCard().play(game=game)


def _sniper_event(game: GameManager) -> None:
    """Discard two Bang! as a single shot requiring two Missed!"""
    SniperEventCard().play(game=game)


def _russian_roulette_event(game: GameManager) -> None:
    """Players discard Missed! or lose 2 life starting from the Sheriff."""
    RussianRouletteEventCard().play(game=game)


def _high_stakes(game: GameManager) -> None:
    """Players may play any number of Bang! cards."""
    HighStakesEventCard().play(game=game)


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
        if game:
            self.apply(game)


def create_high_noon_deck() -> List[BaseEventCard]:
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


def create_fistful_deck() -> List[BaseEventCard]:
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
