"""Handlers for event cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..cards.high_noon_card import HighNoonCard

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


def register(game: "GameManager") -> None:
    """Register handlers for event cards on ``game``."""
    game._card_handlers.update({HighNoonCard: game._handler_self_player_game})
