"""Turn flow helpers for :class:`GameManager`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..characters.jesse_jones import JesseJones
from ..characters.jose_delgado import JoseDelgado
from ..characters.kit_carlson import KitCarlson
from ..characters.pat_brennan import PatBrennan
from ..characters.pedro_ramirez import PedroRamirez
from ..event_flags import EventFlags
from ..game_manager_protocol import GameManagerProtocol

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..player import Player


class TurnFlowMixin:
    """Manage turn progression for :class:`GameManager`."""

    _players: list["Player"]
    turn_order: list[int]
    current_turn: int
    phase: str
    draw_phase_listeners: list
    play_phase_listeners: list
    turn_started_listeners: list
    discard_pile: list
    deck: object
    event_flags: EventFlags

    def play_phase(self: GameManagerProtocol, player: "Player") -> None:
        self.phase = "play"
        for cb in self.play_phase_listeners:
            cb(player)

    # ------------------------------------------------------------------
    # Turn start helpers
    def _handle_equipment_start(self: GameManagerProtocol, player: "Player") -> bool:
        """Process start-of-turn equipment effects."""
        self._reactivate_green_equipment(player)
        if not self._resolve_dynamite(player):
            return False
        return self._process_jail(player)

    def _reactivate_green_equipment(self: GameManagerProtocol, player: "Player") -> None:
        """Refresh green equipment and reapply modifiers."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _resolve_dynamite(self: GameManagerProtocol, player: "Player") -> bool:
        """Handle Dynamite at turn start. Returns ``False`` if the player dies."""
        dyn = player.equipment.get("Dynamite")
        if dyn and hasattr(dyn, "check_dynamite"):
            exploded = dyn.check_dynamite(self, player)
            if exploded:
                self.discard_pile.append(dyn)
                self.on_player_damaged(player)
                if not player.is_alive():
                    self._begin_turn()
                    return False
        return True

    def _process_jail(self: GameManagerProtocol, player: "Player") -> bool:
        """Resolve Jail effects and return ``False`` if the turn is skipped."""
        jail = player.equipment.get("Jail")
        if not jail:
            return True
        if self.event_flags.get("no_jail"):
            player.unequip("Jail")
            self.discard_pile.append(jail)
            return True
        if hasattr(jail, "check_turn"):
            skipped = jail.check_turn(self, player)
            self.discard_pile.append(jail)
            if skipped:
                self.current_turn = (self.current_turn + 1) % len(self.turn_order)
                self._begin_turn()
                return False
        return True

    def _handle_character_draw_abilities(self: GameManagerProtocol, player: "Player") -> bool:
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

    def _begin_turn(self: GameManagerProtocol, *, blood_target: "Player" | None = None) -> None:
        if not self.turn_order:
            return
        self.current_turn %= len(self.turn_order)
        idx = self.turn_order[self.current_turn]
        player = self._players[idx]
        self.phase = "draw"
        self.reset_turn_flags(player)
        next_player: Player | None = self._run_start_turn_checks(player)
        if next_player is None:
            return
        self.draw_phase(next_player, blood_target=blood_target)
        self.play_phase(next_player)
        next_player.metadata.bangs_played = 0
        for cb in self.turn_started_listeners:
            cb(next_player)

    def _run_start_turn_checks(self: GameManagerProtocol, player: "Player") -> "Player" | None:
        """Apply start-of-turn effects returning the acting player or ``None``."""
        next_player: Player | None = self._apply_event_start_effects(player)
        if next_player is None:
            return None
        if self._maybe_revive_ghost_town(next_player):
            return None
        if not self._handle_equipment_start(next_player):
            return None
        if self._handle_character_draw_abilities(next_player):
            return None
        return next_player

    def end_turn(self: GameManagerProtocol) -> None:
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
    def _reset_green_equipment(self: GameManagerProtocol, player: "Player") -> None:
        """Reactivate green equipment at the end of the turn."""
        for eq in list(player.equipment.values()):
            if eq.card_type == "green" and not getattr(eq, "active", True):
                eq.active = True
                modifier = int(getattr(eq, "max_health_modifier", 0))
                if modifier:
                    player._apply_health_modifier(modifier)

    def _advance_turn(self: GameManagerProtocol) -> None:
        """Move the turn pointer and start the next turn."""
        if self.event_flags.get("reverse_turn"):
            self.current_turn = (self.current_turn - 1) % len(self.turn_order)
        else:
            self.current_turn = (self.current_turn + 1) % len(self.turn_order)
        self._begin_turn()
