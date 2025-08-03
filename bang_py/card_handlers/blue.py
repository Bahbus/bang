"""Handlers for blue (equipment) cards.

Currently blue cards require no special handling beyond the default play
behaviour, so this module registers nothing."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager


def register(game: 'GameManager') -> None:  # pragma: no cover - simple passthrough
    """Register handlers for blue cards on ``game`` (currently none)."""
    return None
