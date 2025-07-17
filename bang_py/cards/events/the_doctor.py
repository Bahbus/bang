from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class TheDoctorEventCard(BaseEventCard):
    """Heal the weakest player(s) by one life."""

    card_name = "The Doctor"
    card_set = "high_noon"
    description = (
        "When The Doctor enters play, the player(s) still in the game with the fewest "
        "life points regain 1 life point."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        """Activate the The Doctor event."""
        if not game:
            return
        alive = [p for p in game.players if p.is_alive()]
        if not alive:
            return
        min_hp = min(p.health for p in alive)
        for p in alive:
            if p.health == min_hp and p.health < p.max_health:
                before = p.health
                p.heal(1)
                if p.health > before:
                    game.on_player_healed(p)
