"""Protocol declaring the GameManager interface used by mixins."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable
from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from .cards.card import BaseCard
    from .cards.roles import BaseRole
    from .characters.base import BaseCharacter
    from .deck import Deck
    from .events.event_decks import EventCard
    from .player import Player


class GameManagerProtocol(Protocol):
    """Attributes and methods shared across GameManager mixins."""

    deck: Deck | None
    discard_pile: list[BaseCard]
    event_flags: dict[str, object]
    expansions: list[str]
    _players: list[Player]
    turn_order: list[int]
    current_turn: int
    event_deck: deque[EventCard] | None
    current_event: EventCard | None
    first_eliminated: Player | None
    sheriff_turns: int
    phase: str
    general_store_cards: list[BaseCard] | None
    general_store_order: list[Player] | None
    general_store_index: int
    draw_phase_listeners: list[Callable[[Player, object], bool]]
    play_phase_listeners: list[Callable[[Player], None]]
    turn_started_listeners: list[Callable[[Player], None]]
    card_play_checks: list[Callable[[Player, BaseCard, Player | None], bool]]
    card_played_listeners: list[Callable[[Player, BaseCard, Player | None], None]]
    _card_handlers: dict

    def draw_card(self, player: Player, num: int = 1) -> None:
        """Draw ``num`` cards for ``player``."""

    def _draw_from_deck(self) -> BaseCard | None:
        """Draw a single card from the deck."""

    def _pass_left_or_discard(self, player: Player, card: BaseCard) -> None:
        """Discard ``card`` or pass it left based on active events."""

    def _hand_limit(self, player: Player) -> int:
        """Return the maximum hand size for ``player``."""

    def _discard_to_limit(self, player: Player, limit: int) -> None:
        """Discard cards from ``player`` until ``limit`` is met."""

    def discard_card(self, player: Player, card: BaseCard) -> None:
        """Remove ``card`` from ``player``'s hand and discard it."""

    def play_card(self, player: Player, card: BaseCard, target: Player | None = None) -> None:
        """Play ``card`` from ``player`` targeting ``target`` if provided."""

    def on_player_damaged(self, player: Player, source: Player | None = None) -> None:
        """Handle ``player`` taking damage from ``source``."""

    def on_player_healed(self, player: Player) -> None:
        """Handle ``player`` regaining health."""

    def _begin_turn(self, *, blood_target: Player | None = None) -> None:
        """Start a new turn, optionally applying Blood Brothers."""

    def _check_win_conditions(self) -> None:
        """Verify whether the game has ended."""

    def _deal_general_store_cards(self) -> list[BaseCard]:
        """Deal cards for the General Store."""

    def _set_general_store_order(self, player: Player) -> None:
        """Initialize General Store pick order starting with ``player``."""

    def _valid_general_store_pick(self, player: Player, index: int) -> bool:
        """Return ``True`` if ``player`` can take the card at ``index``."""

    def _cleanup_general_store_leftovers(self) -> None:
        """Discard any remaining General Store cards and reset state."""

    def reset_turn_flags(self, player: Player) -> None:
        """Reset per-turn ability flags on ``player``."""

    def discard_phase(self, player: Player) -> None:
        """Execute the discard phase for ``player``."""

    def draw_phase(self, player: Player, **kwargs: object) -> None:
        """Execute the draw phase for ``player``."""

    def play_phase(self, player: Player) -> None:
        """Execute the play phase for ``player``."""

    def _apply_event_start_effects(self, player: Player) -> Player | None:
        """Apply start-of-turn event effects returning the acting player."""

    def _reactivate_green_equipment(self, player: Player) -> None:
        """Reactivate green equipment on ``player``."""

    def _resolve_dynamite(self, player: Player) -> bool:
        """Return ``False`` if Dynamite eliminates ``player``."""

    def _run_start_turn_checks(self, player: Player) -> Player | None:
        """Run start-of-turn checks returning the acting player or ``None``."""

    def _maybe_revive_ghost_town(self, player: Player) -> bool:
        """Return True if Ghost Town revives ``player``."""

    def _handle_vendetta(self, player: Player) -> bool:
        """Return True if the Vendetta event skips the turn."""

    def _finish_ghost_town(self, player: Player) -> None:
        """Finalize Ghost Town effects on ``player``."""

    def prompt_new_identity(self, player: Player) -> bool:
        """Prompt ``player`` to swap characters during New Identity."""

    def _pre_card_checks(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Return ``True`` if ``player`` may play ``card`` on ``target``."""

    def _is_bang(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Return ``True`` if playing ``card`` counts as a Bang!."""

    def _dispatch_play(self, player: Player, card: BaseCard, target: Player | None) -> None:
        """Dispatch ``card`` to its handler."""

    def _update_bang_counters(self, player: Player) -> None:
        """Update per-turn Bang! counters for ``player``."""

    def _current_player_obj(self) -> Player | None:
        """Return the player whose turn it currently is."""

    def _reindex_turn_order(self, removed_idx: int) -> None:
        """Rebuild turn order after removing ``removed_idx``."""

    def _build_role_deck(self) -> list[type[BaseRole]]:
        """Return role classes for the current player count."""

    def _build_character_deck(self) -> list[type[BaseCharacter]]:
        """Return available character classes."""

    def choose_character(self, player: Player, options: list[BaseCharacter]) -> BaseCharacter:
        """Select the character for ``player`` from ``options``."""

    def _deal_roles_and_characters(self) -> None:
        """Assign roles and characters to all players."""

    def _next_alive_player(self, player: Player) -> Player | None:
        """Return the next living player to the left of ``player``."""

    def _get_player_by_index(self, idx: int) -> Player | None:
        """Return the player at ``idx`` if it exists."""


__all__ = ["GameManagerProtocol"]
