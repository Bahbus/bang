"""Protocol declaring the GameManager interface used by mixins."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable, Sequence
from typing import Protocol, TYPE_CHECKING

from .event_flags import EventFlags

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
    event_flags: EventFlags
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
    # Event listeners
    draw_phase_listeners: list[Callable[[Player, object], bool]]
    play_phase_listeners: list[Callable[[Player], None]]
    turn_started_listeners: list[Callable[[Player], None]]
    card_play_checks: list[Callable[[Player, BaseCard, Player | None], bool]]
    card_played_listeners: list[Callable[[Player, BaseCard, Player | None], None]]
    player_damaged_listeners: list[Callable[[Player, Player | None], None]]
    player_healed_listeners: list[Callable[[Player], None]]
    player_death_listeners: list[Callable[[Player, Player | None], None]]
    game_over_listeners: list[Callable[[str], None]]
    _card_handlers: dict
    _duel_counts: dict | None

    @property
    def players(self) -> Sequence[Player]:
        """Players in turn order."""
        ...

    def initialize_main_deck(self) -> None:
        """Create the main deck and reset event flags."""

    def initialize_event_deck(self) -> None:
        """Build and shuffle the event deck based on expansions."""

    def register_card_handlers(self, groups: Iterable[str] | None = None) -> None:
        """Populate the card handler registry."""

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

    def _notify_damage_listeners(self, player: Player, source: Player | None) -> None:
        """Inform damage listeners of health loss."""

    def _handle_ghost_town_revive(self, player: Player) -> bool:
        """Return True if Ghost Town revives ``player``."""

    def _record_first_elimination(self, player: Player) -> None:
        """Record the first eliminated player."""

    def _bounty_reward(self, source: Player | None) -> None:
        """Award Bounty rewards to ``source`` if applicable."""

    def _notify_death_listeners(self, player: Player, source: Player | None) -> None:
        """Inform listeners that ``player`` has been eliminated."""

    def _update_turn_order_post_death(self) -> None:
        """Adjust turn order after a player is eliminated."""

    def _determine_winner(self, alive: list[Player], has_sheriff: bool) -> str | None:
        """Return a victory message if a win condition is met."""

    def get_hand(self, viewer: Player, target: Player) -> list[str]:
        """Return the visible hand of ``target`` for ``viewer``."""

    def _begin_turn(self, *, blood_target: Player | None = None) -> None:
        """Start a new turn, optionally applying Blood Brothers."""

    def _check_win_conditions(self) -> str | None:
        """Return a victory message if the game has ended."""

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

    def _process_jail(self, player: Player) -> bool:
        """Resolve Jail effects and return ``False`` if the turn is skipped."""

    def _handle_equipment_start(self, player: Player) -> bool:
        """Process start-of-turn equipment effects."""

    def _handle_character_draw_abilities(self, player: Player) -> bool:
        """Trigger characters that modify the draw phase."""

    def _run_start_turn_checks(self, player: Player) -> Player | None:
        """Run start-of-turn checks returning the acting player or ``None``."""

    def _maybe_revive_ghost_town(self, player: Player) -> bool:
        """Return True if Ghost Town revives ``player``."""

    def _handle_vendetta(self, player: Player) -> bool:
        """Return True if the Vendetta event skips the turn."""

    def _finish_ghost_town(self, player: Player) -> None:
        """Finalize Ghost Town effects on ``player``."""

    def _reset_green_equipment(self, player: Player) -> None:
        """Reactivate green equipment at the end of the turn."""

    def _advance_turn(self) -> None:
        """Move the turn pointer and start the next turn."""

    def prompt_new_identity(self, player: Player) -> bool:
        """Prompt ``player`` to swap characters during New Identity."""

    def _pre_card_checks(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Return ``True`` if ``player`` may play ``card`` on ``target``."""

    def _card_in_hand(self, player: Player, card: BaseCard) -> bool:
        """Return ``True`` if ``card`` is currently in ``player``'s hand."""

    def _run_card_play_checks(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Execute registered pre-play checks."""

    def _check_target_restrictions(
        self, player: Player, card: BaseCard, target: Player | None
    ) -> bool:
        """Validate distance and target based limitations."""

    def _bang_target_valid(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Check range and sniper restrictions for Bang! cards."""

    def _panic_target_valid(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Return ``True`` if Panic! can target ``target``."""

    def _jail_target_valid(self, card: BaseCard, target: Player | None) -> bool:
        """Return ``True`` if Jail may be played on ``target``."""

    def _check_event_restrictions(self, player: Player, card: BaseCard) -> bool:
        """Check event related card play restrictions."""

    def _jail_blocked(self, card: BaseCard) -> bool:
        """Return ``True`` if Jail cards are currently banned."""

    def _judge_blocked(self, card: BaseCard) -> bool:
        """Return ``True`` if blue or green cards are disallowed."""

    def _handcuffs_blocked(self, player: Player, card: BaseCard) -> bool:
        """Return ``True`` if Handcuffs prevents ``player`` from playing ``card``."""

    def _is_bang(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Return ``True`` if playing ``card`` counts as a Bang!."""

    def _handle_missed_as_bang(self, player: Player, card: BaseCard, target: Player | None) -> bool:
        """Treat Missed! cards as Bang! when allowed."""

    def _can_play_bang(self, player: Player) -> bool:
        """Return ``True`` if ``player`` may play a Bang!."""

    def _dispatch_play(self, player: Player, card: BaseCard, target: Player | None) -> None:
        """Dispatch ``card`` to its handler."""

    def _notify_card_played(self, player: Player, card: BaseCard, target: Player | None) -> None:
        """Call registered card played listeners."""

    def _apply_post_play(
        self,
        player: Player,
        card: BaseCard,
        target: Player | None,
        before: int | None,
        is_bang: bool,
    ) -> None:
        """Handle aftermath of playing ``card``."""

    def _apply_damage_and_healing(
        self, source: Player, target: Player | None, before: int | None
    ) -> None:
        """Trigger damage or heal callbacks if ``target`` changed health."""

    def _draw_if_empty(self, player: Player) -> None:
        """Draw a card if ``player`` has an empty hand and may draw."""

    def _discard_and_record(self, player: Player, card: BaseCard) -> None:
        """Discard ``card`` from ``player`` and record out-of-turn discard."""

    def _should_use_auto_miss(self, target: Player) -> bool:
        """Return ``True`` if automatic Missed! effects may apply."""

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

    def _reset_current_turn(self, current_obj: Player | None) -> None:
        """Adjust ``current_turn`` when removing a player."""


__all__ = ["GameManagerProtocol"]
