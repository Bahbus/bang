from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager import GameManager


class NewIdentityEventCard(BaseEventCard):
    """At the start of their turn, each player may look at their other face down
    character card and switch to it with 2 life."""

    card_name = "New Identity"
    card_set = "high_noon"
    description = (
        "At the start of their turn, each player may look at their other face down "
        "character card and switch to it with 2 life."
    )

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        if game:
            game.event_flags["new_identity"] = True
