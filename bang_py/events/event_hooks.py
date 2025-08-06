"""Event notification and win condition helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.roles import SheriffRoleCard
from ..cards.card import BaseCard

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from ..player import Player
    from ..game_manager import GameManager


class EventHooksMixin:
    """Provide event callbacks and win condition checks."""

    _players: list[Player]
    turn_order: list[int]
    current_turn: int
    event_flags: dict
    discard_pile: list[BaseCard]
    first_eliminated: Player | None
    game_over_listeners: list
    player_damaged_listeners: list
    player_death_listeners: list
    player_healed_listeners: list

    def on_player_damaged(
        self, player: Player, source: Player | None = None
    ) -> None:
        """Handle player damage and determine if they are eliminated."""
        self._notify_damage_listeners(player, source)
        if player.health > 0:
            return
        if self._handle_ghost_town_revive(player):
            return
        self._record_first_elimination(player)
        self._bounty_reward(source)
        self._notify_death_listeners(player, source)
        self._check_win_conditions()

    def _notify_damage_listeners(
        self, player: Player, source: Player | None
    ) -> None:
        for cb in self.player_damaged_listeners:
            cb(player, source)

    def _bounty_reward(self, source: Player | None) -> None:
        if source and self.event_flags.get("bounty"):
            self.draw_card(source, 2)

    def _notify_death_listeners(
        self, player: Player, source: Player | None
    ) -> None:
        for cb in self.player_death_listeners:
            cb(player, source)

    def _handle_ghost_town_revive(self, player: Player) -> bool:
        """Revive a Ghost Town player if possible."""
        if self.event_flags.get("ghost_town") and player.metadata.ghost_revived:
            player.health = 1
            return True
        return False

    def _record_first_elimination(self, player: Player) -> None:
        if self.first_eliminated is None:
            self.first_eliminated = player

    def on_player_healed(self, player: Player) -> None:
        """Notify listeners that ``player`` has regained health."""
        for cb in self.player_healed_listeners:
            cb(player)

    def blood_brothers_transfer(
        self, donor: Player, target: Player
    ) -> bool:
        """Transfer one life from ``donor`` to ``target`` if allowed."""
        if not self.event_flags.get("blood_brothers"):
            return False
        if donor.health <= 1 or donor not in self._players or target not in self._players:
            return False
        donor.take_damage(1)
        self.on_player_damaged(donor)
        if not donor.is_alive():
            return True
        target.heal(1)
        self.on_player_healed(target)
        return True

    def _check_win_conditions(self) -> str | None:
        alive = [p for p in self._players if p.is_alive()]
        self._update_turn_order_post_death()
        has_sheriff = any(
            isinstance(p.role, SheriffRoleCard) for p in self._players
        )
        result = self._determine_winner(alive, has_sheriff)
        if result:
            for cb in self.game_over_listeners:
                cb(result)
        return result

    # ------------------------------------------------------------------
    # Win condition helpers
    def _update_turn_order_post_death(self) -> None:
        """Remove eliminated players from turn order and adjust the index."""
        self.turn_order = [i for i in self.turn_order if self._players[i].is_alive()]
        if self.turn_order:
            self.current_turn %= len(self.turn_order)
        else:
            self.current_turn = 0

    def _determine_winner(
        self, alive: list[Player], has_sheriff: bool
    ) -> str | None:
        """Return a victory message if a win condition is met."""
        if not has_sheriff and len(self._players) == 3:
            if len(alive) == 1 and alive[0].role:
                return alive[0].role.victory_message
            return None
        for player in alive:
            if player.role and player.role.check_win(self, player):
                return player.role.victory_message
        return None

    def get_hand(self, viewer: Player, target: Player) -> list[str]:
        """Return the visible hand of ``target`` for ``viewer``."""
        if viewer is target or self.event_flags.get("revealed_hands"):
            return [c.card_name for c in target.hand]
        return ["?" for _ in target.hand]
