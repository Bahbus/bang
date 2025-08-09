"""Orchestrator class composing game subsystems."""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Callable, Iterable, Sequence
from collections import deque
from typing import cast

from .ability_dispatch import AbilityDispatchMixin
from .card_handlers import CardHandlersMixin
from .cards.card import BaseCard
from .deck import Deck
from .deck_manager import DeckManagerMixin
from .event_flags import EventFlags
from .events.event_decks import EventCard
from .events.event_hooks import EventHooksMixin
from .events.event_logic import EventLogicMixin
from .general_store import GeneralStoreMixin
from .game_manager_protocol import GameManagerProtocol
from .player import Player
from .turn_phases import TurnPhasesMixin


@dataclass(slots=True)
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
    event_flags: EventFlags = field(default_factory=lambda: cast(EventFlags, {}))
    first_eliminated: Player | None = None
    sheriff_turns: int = 0
    phase: str = "draw"

    # General Store state
    general_store_cards: list[BaseCard] | None = None
    general_store_order: list[Player] | None = None
    general_store_index: int = 0

    # Event listeners
    draw_phase_listeners: list[Callable[[Player, object], bool]] = field(default_factory=list)
    player_damaged_listeners: list[Callable[[Player, Player | None], None]] = field(
        default_factory=list
    )
    player_healed_listeners: list[Callable[[Player], None]] = field(default_factory=list)
    player_death_listeners: list[Callable[[Player, Player | None], None]] = field(
        default_factory=list
    )
    turn_started_listeners: list[Callable[[Player], None]] = field(default_factory=list)
    game_over_listeners: list[Callable[[str], None]] = field(default_factory=list)
    card_play_checks: list[Callable[[Player, BaseCard, Player | None], bool]] = field(
        default_factory=list
    )
    card_played_listeners: list[Callable[[Player, BaseCard, Player | None], None]] = field(
        default_factory=list
    )
    play_phase_listeners: list[Callable[[Player], None]] = field(default_factory=list)
    _card_handlers: dict = field(default_factory=dict, init=False, repr=False)
    _duel_counts: dict | None = field(default=None, init=False, repr=False)

    @property
    def players(self) -> Sequence[Player]:
        """Players in turn order as a read-only sequence."""
        return tuple(self._players)

    def prompt_new_identity(self, player: Player) -> bool:
        """Return True if the player opts to switch characters."""
        return True

    # ------------------------------------------------------------------
    # Protocol wrappers
    def initialize_main_deck(self) -> None:
        """Create the main deck and reset event flags."""
        gm: GameManagerProtocol = cast(GameManagerProtocol, self)
        gm._initialize_main_deck()

    def initialize_event_deck(self) -> None:
        """Build the event deck based on active expansions."""
        gm: GameManagerProtocol = cast(GameManagerProtocol, self)
        gm._initialize_event_deck()

    def register_card_handlers(self, groups: Iterable[str] | None = None) -> None:
        """Populate the card handler registry."""
        gm: GameManagerProtocol = cast(GameManagerProtocol, self)
        gm._register_card_handlers(groups)

    def start_general_store(self, player: Player) -> list[str]:
        """Deal cards for the General Store and establish the pick order."""
        gm: GameManagerProtocol = cast(GameManagerProtocol, self)
        if not gm.deck:
            gm.general_store_cards = []
            gm.general_store_order = []
            gm.general_store_index = 0
            return []
        cards = gm._deal_general_store_cards()
        gm.general_store_cards = cards
        gm._set_general_store_order(player)
        return [c.card_name for c in cards]

    def general_store_pick(self, player: Player, index: int) -> bool:
        """Allow ``player`` to take a card from the General Store."""
        gm: GameManagerProtocol = cast(GameManagerProtocol, self)
        if not gm._valid_general_store_pick(player, index):
            return False
        cards = gm.general_store_cards
        order = gm.general_store_order
        if cards is None or order is None:
            return False
        card = cards.pop(index)
        player.hand.append(card)
        gm.general_store_index += 1
        if gm.general_store_index >= len(order):
            gm._cleanup_general_store_leftovers()
        return True

    def _handle_missed_as_bang(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Treat Missed! cards as Bang."""
        return super(GameManager, self)._handle_missed_as_bang(player, card, target)

    def _advance_turn(self) -> None:
        """Advance to the next player's turn."""
        super(GameManager, self)._advance_turn()

    def pat_brennan_draw(
        self, player: Player, target: Player | None = None, card: str | None = None
    ) -> bool:
        """Handle Pat Brennan's draw ability."""
        return super(GameManager, self).pat_brennan_draw(player, target, card)

    def __post_init__(self) -> None:
        """Initialize decks and register card handlers."""
        self.initialize_main_deck()
        self.initialize_event_deck()
        self.register_card_handlers()
