"""Orchestrator class composing game subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Callable, Sequence
from collections import deque

from .deck import Deck
from .cards.card import BaseCard
from .player import Player
from .events.event_decks import EventCard
from .events.event_logic import EventLogicMixin
from .card_handlers import CardHandlersMixin
from .general_store import GeneralStoreMixin
from .turn_phases import TurnPhasesMixin
from .deck_manager import DeckManagerMixin
from .ability_dispatch import AbilityDispatchMixin
from .events.event_hooks import EventHooksMixin


@dataclass
class GameManager(
    DeckManagerMixin,
    AbilityDispatchMixin,
    EventHooksMixin,
    EventLogicMixin,
    CardHandlersMixin,
    GeneralStoreMixin,
    TurnPhasesMixin,
):
    """Coordinate game state, players and turn progression."""

    _players: list[Player] = field(default_factory=list)
    deck: Deck | None = None
    expansions: list[str] = field(default_factory=list)
    discard_pile: list[BaseCard] = field(default_factory=list)
    current_turn: int = 0
    turn_order: list[int] = field(default_factory=list)
    event_deck: deque[EventCard] | None = None
    current_event: EventCard | None = None
    event_flags: dict = field(default_factory=dict)
    first_eliminated: Player | None = None
    sheriff_turns: int = 0
    phase: str = "draw"

    # General Store state
    general_store_cards: list[BaseCard] | None = None
    general_store_order: list[Player] | None = None
    general_store_index: int = 0

    # Event listeners
    draw_phase_listeners: list[Callable[[Player, object], bool]] = field(
        default_factory=list
    )
    player_damaged_listeners: list[Callable[[Player, Player | None], None]] = field(
        default_factory=list
    )
    player_healed_listeners: list[Callable[[Player], None]] = field(
        default_factory=list
    )
    player_death_listeners: list[Callable[[Player, Player | None], None]] = field(
        default_factory=list
    )
    turn_started_listeners: list[Callable[[Player], None]] = field(default_factory=list)
    game_over_listeners: list[Callable[[str], None]] = field(default_factory=list)
    card_play_checks: list[Callable[[Player, BaseCard, Player | None], bool]] = field(
        default_factory=list
    )
    card_played_listeners: list[
        Callable[[Player, BaseCard, Player | None], None]
    ] = field(default_factory=list)
    play_phase_listeners: list[Callable[[Player], None]] = field(default_factory=list)
    _duel_counts: dict | None = field(default=None, init=False, repr=False)

    @property
    def players(self) -> Sequence[Player]:
        """Players in turn order as a read-only sequence."""
        return tuple(self._players)

    def prompt_new_identity(self, player: Player) -> bool:
        """Return True if the player opts to switch characters."""
        return True

    def __post_init__(self) -> None:
        """Initialize decks and register card handlers."""
        self._initialize_main_deck()
        self._initialize_event_deck()
        self._register_card_handlers()
