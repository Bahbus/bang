"""Train Arrival card from the High Noon expansion. During their draw phase, each player draws an
additional card."""

from __future__ import annotations

from .base import BaseEventCard
from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...game_manager_protocol import GameManagerProtocol


class TrainArrivalEventCard(BaseEventCard):
    """Players draw one additional card during the draw phase."""

    card_name = "Train Arrival"
    card_set = "high_noon"
    description = "During their draw phase, each player draws an additional card."

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
    ) -> None:
        """Activate the Train Arrival event."""
        if game:
            game.event_flags["draw_count"] = 3
