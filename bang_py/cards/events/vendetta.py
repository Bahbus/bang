from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class VendettaEventCard(BaseEventCard):
    """Outlaws gain +1 attack range."""

    card_name = "Vendetta"
    description = "Outlaws have +1 range"

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["vendetta"] = True
