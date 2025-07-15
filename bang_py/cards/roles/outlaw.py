from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseRole

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ...game_manager import GameManager
    from ...player import Player


class OutlawRoleCard(BaseRole):
    """Role card representing an Outlaw."""

    card_name = "Outlaw"
    victory_message = "Outlaws win!"

    def check_win(self, gm: GameManager, player: Player) -> bool:
        from .sheriff import SheriffRoleCard

        return not any(
            isinstance(p.role, SheriffRoleCard) and p.is_alive() for p in gm.players
        )
