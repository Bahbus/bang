from __future__ import annotations

from ...player import Player
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints
    from ...game_manager import GameManager


class BaseEventCard:
    """Common base for simple event cards."""

    card_name: str = "Event"
    card_type = "event"
    card_set = "event_deck"
    description: str = ""

    @property
    def name(self) -> str:
        """Compatibility alias for ``card_name``."""
        return self.card_name

    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManager | None = None,
    ) -> None:
        raise NotImplementedError

    def apply(self, game: GameManager) -> None:
        """Execute this event's effect."""
        self.play(game=game)
