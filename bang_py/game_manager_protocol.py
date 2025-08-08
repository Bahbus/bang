"""Protocols for :class:`GameManager` interactions across mixins."""

from __future__ import annotations

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imported for type checking
    from .player import Player
    from .cards.card import BaseCard


class GameManagerProtocol(Protocol):
    """Interface exposing cross-mixin hooks used by ``GameManager``."""

    def draw_card(self, player: "Player", num: int = 1) -> None:
        """Draw ``num`` cards for ``player``."""

    def _pass_left_or_discard(self, player: "Player", card: "BaseCard") -> None:
        """Discard ``card`` or pass it left depending on events."""

    def play_card(
        self,
        player: "Player",
        card: "BaseCard",
        target: "Player" | None = None,
    ) -> None:
        """Play ``card`` from ``player`` targeting ``target`` if provided."""

    def on_player_damaged(self, player: "Player", source: "Player" | None = None) -> None:
        """Handle damage taken by ``player`` from ``source``."""

    def on_player_healed(self, player: "Player") -> None:
        """Handle ``player`` regaining health."""


__all__ = ["GameManagerProtocol"]
