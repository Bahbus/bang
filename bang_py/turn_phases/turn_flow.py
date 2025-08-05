"""Turn flow helpers for :class:`GameManager`."""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from ..characters.jesse_jones import JesseJones
from ..characters.jose_delgado import JoseDelgado
from ..characters.kit_carlson import KitCarlson
from ..characters.pat_brennan import PatBrennan
from ..characters.pedro_ramirez import PedroRamirez

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..player import Player
    from ..game_manager import GameManager


class TurnFlowMixin:
    """Manage turn progression for :class:`GameManager`."""

    _players: List['Player']
    turn_order: List[int]
    current_turn: int
    phase: str
    draw_phase_listeners: List
    play_phase_listeners: List
    turn_started_listeners: List
    discard_pile: list
    deck: object
    event_flags: dict

    def play_phase(self: 'GameManager', player: 'Player') -> None:
        self.phase = "play"
        for cb in self.play_phase_listeners:
            cb(player)

    # ------------------------------------------------------------------
    # Turn start helpers
    def _handle_equipment_start(self: 'GameManager', player: 'Player') -> bool:
        """Process start-of-turn equipment effects."""
        self._reactivate_green_equipment(player)
        if not self._resolve_dynamite(player):
            return False
        return self._process_jail(player)

    def _reactivate_green_equipment(self: 'GameManager', player: 'Player') -> None:
        """Refresh green equipment and reapply modifiers."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _resolve_dynamite(self: 'GameManager', player: 'Player') -> bool:
        """Handle Dynamite at turn start. Returns ``False`` if the player dies."""
        dyn = player.equipment.get("Dynamite")
        if dyn and getattr(dyn, "check_dynamite", None):
            next_idx = self.turn_order[(self.current_turn + 1) % len(self.turn_order)]
            next_player = self._players[next_idx]
            exploded = dyn.check_dynamite(player, next_player, self.deck)
            if exploded:
                self.discard_pile.append(dyn)
                self.on_player_damaged(player)
                if not player.is_alive():
                    self._begin_turn()
                    return False
        return True

    def _process_jail(self: 'GameManager', player: 'Player') -> bool:
        """Resolve Jail effects and return ``False`` if the turn is skipped."""
        jail = player.equipment.get("Jail")
        if not jail:
            return True
        if self.event_flags.get("no_jail"):
            player.unequip("Jail")
            self.discard_pile.append(jail)
            return True
        if getattr(jail, "check_turn", None):
            skipped = jail.check_turn(player, self.deck)
            self.discard_pile.append(jail)
            if skipped:
                self.current_turn = (self.current_turn + 1) % len(self.turn_order)
                self._begin_turn()
                return False
        return True

    def _handle_character_draw_abilities(
        self: 'GameManager', player: 'Player'
    ) -> bool:
        """Trigger characters that modify the draw phase."""
        ability_chars = (
            JesseJones,
            KitCarlson,
            PedroRamirez,
            JoseDelgado,
            PatBrennan,
        )
        if isinstance(player.character, ability_chars):
            player.metadata.awaiting_draw = True
            for cb in self.turn_started_listeners:
                cb(player)
            return True
        return False

    def _begin_turn(self: 'GameManager', *, blood_target: Optional['Player'] = None) -> None:
        if not self.turn_order:
            return
        self.current_turn %= len(self.turn_order)
        idx = self.turn_order[self.current_turn]
        player = self._players[idx]
        self.phase = "draw"
        self.reset_turn_flags(player)
        player = self._run_start_turn_checks(player)
        if not player:
            return
        self.draw_phase(player, blood_target=blood_target)
        self.play_phase(player)
        player.metadata.bangs_played = 0
        for cb in self.turn_started_listeners:
            cb(player)

    def _run_start_turn_checks(
        self: 'GameManager', player: 'Player'
    ) -> Optional['Player']:
        """Apply start-of-turn effects returning the acting player or ``None``."""
        player = self._apply_event_start_effects(player)
        if not player:
            return None
        if self._maybe_revive_ghost_town(player):
            return None
        if not self._handle_equipment_start(player):
            return None
        if self._handle_character_draw_abilities(player):
            return None
        return player

    def end_turn(self: 'GameManager') -> None:
        """Finish the current player's turn and advance to the next."""
        if not self.turn_order:
            return
        idx = self.turn_order[self.current_turn]
        player = self._players[idx]
        self.phase = "discard"
        self.discard_phase(player)
        self.event_flags.pop("turn_suit", None)
        self._reset_green_equipment(player)
        if self._handle_vendetta(player):
            return
        self._finish_ghost_town(player)
        self._advance_turn()

    # ------------------------------------------------------------------
    # Turn end helpers
    def _reset_green_equipment(self: 'GameManager', player: 'Player') -> None:
        """Reactivate green equipment at the end of the turn."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _advance_turn(self: 'GameManager') -> None:
        """Move the turn pointer and start the next turn."""
        if self.event_flags.get("reverse_turn"):
            self.current_turn = (self.current_turn - 1) % len(self.turn_order)
        else:
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        self._begin_turn()
