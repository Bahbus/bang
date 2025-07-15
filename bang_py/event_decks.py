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
)
from .player import Player

if TYPE_CHECKING:
    from .game_manager import GameManager


def _peyote(game: GameManager) -> None:
    """During their draw phase, instead of drawing, each player guesses red or black. They draw and reveal; if correct they may guess again."""
    PeyoteEventCard().play(game=game)


def _ricochet(game: GameManager) -> None:
    """Each player may discard Bang! cards to target cards in play. The target card is discarded unless its owner plays a Missed!"""
    RicochetEventCard().play(game=game)





def _judge(game: GameManager) -> None:
    """Players cannot play cards in front of themselves or others."""
    TheJudgeEventCard().play(game=game)


def _ghost_town(game: GameManager) -> None:
    """During their turn, eliminated players return as ghosts with 3 cards and cannot die. They are eliminated again at turn end."""
    GhostTownEventCard().play(game=game)



def _vendetta(game: GameManager) -> None:
    """At the end of their turn, each player draws! If it's a heart, they immediately take another turn. This can occur only once per player."""
    VendettaEventCard().play(game=game)


def _thirst(game: GameManager) -> None:
    """During their draw phase, each player draws only their first card."""
    ThirstEventCard().play(game=game)


def _shootout(game: GameManager) -> None:
    """Each player may play a second Bang! card during their turn."""
    ShootoutEventCard().play(game=game)


def _high_noon(game: GameManager) -> None:
    """Each player loses 1 life point at the start of their turn."""
    HighNoonEventCard().play(game=game)


def _fistful(game: GameManager) -> None:
    """At the beginning of each turn, target the active player with Bang! once for each card in their hand."""
    FistfulOfCardsEventCard().play(game=game)


def _blessing(game: GameManager) -> None:
    """The suit of all cards is hearts."""
    BlessingEventCard().play(game=game)


def _gold_rush(game: GameManager) -> None:
    """The game proceeds counter-clockwise, but card effects still proceed clockwise."""
    GoldRushEventCard().play(game=game)


def _law_of_the_west(game: GameManager) -> None:
    """During the draw phase, each player reveals the second card they drew and plays it immediately if possible."""
    LawOfTheWestEventCard().play(game=game)




def _sermon(game: GameManager) -> None:
    """Each player cannot use Bang! cards during their turn."""
    TheSermonEventCard().play(game=game)


def _hangover(game: GameManager) -> None:
    """All characters lose their abilities."""
    HangoverEventCard().play(game=game)


def _abandoned_mine(game: GameManager) -> None:
    """During their draw phase, players draw from the discard pile instead. During their discard phase, cards are placed face down on top of the deck."""
    AbandonedMineEventCard().play(game=game)


def _ambush_event(game: GameManager) -> None:
    """The distance between any two players is 1. Only other cards in play may modify this."""
    AmbushEventCard().play(game=game)


def _ranch(game: GameManager) -> None:
    """At the end of their draw phase, each player may once discard any number of cards and draw the same number."""
    RanchEventCard().play(game=game)


def _hard_liquor(game: GameManager) -> None:
    """Each player may skip their draw phase to regain 1 life."""
    HardLiquorEventCard().play(game=game)


def _blood_brothers(game: GameManager) -> None:
    """At the beginning of each turn, a player may lose 1 life (not their last) to give 1 life to any player."""
    BloodBrothersEventCard().play(game=game)





def _daltons_event(game: GameManager) -> None:
    """When The Daltons enters play, each player with blue cards discards one."""
    TheDaltonsEventCard().play(game=game)


def _doctor_event(game: GameManager) -> None:
    """When The Doctor enters play, the player(s) with the fewest life points regain 1 life."""
    TheDoctorEventCard().play(game=game)


def _reverend_event(game: GameManager) -> None:
    """Players cannot play Beer cards."""
    TheReverendEventCard().play(game=game)


def _train_arrival_event(game: GameManager) -> None:
    """During their draw phase, each player draws an additional card."""
    TrainArrivalEventCard().play(game=game)


def _handcuffs_event(game: GameManager) -> None:
    """After drawing, each player chooses a suit and can only play that suit for the rest of their turn."""
    HandcuffsEventCard().play(game=game)


def _new_identity_event(game: GameManager) -> None:
    """At the start of their turn, a player may look at their other character and switch to it with 2 life."""
    NewIdentityEventCard().play(game=game)


def _lasso_event(game: GameManager) -> None:
    """Cards in play in front of players have no effect."""
    LassoEventCard().play(game=game)


def _sniper_event(game: GameManager) -> None:
    """During their turn, a player may discard two Bang! cards as one attack that requires two Missed!"""
    SniperEventCard().play(game=game)


def _russian_roulette_event(game: GameManager) -> None:
    """When Russian Roulette enters play, starting with the Sheriff each player discards a Missed!. The first who cannot loses 2 life points."""
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
