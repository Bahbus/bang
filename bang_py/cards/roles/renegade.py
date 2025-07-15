from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseRole

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ...game_manager import GameManager
    from ...player import Player


class RenegadeRoleCard(BaseRole):
    """Role card representing the Renegade."""

    card_name = "Renegade"
    victory_message = "Renegade wins!"

    def check_win(self, gm: GameManager, player: Player) -> bool:
        from .sheriff import SheriffRoleCard

        alive = [p for p in gm.players if p.is_alive()]
        return len(alive) == 1 and alive[0] is player and not any(
            isinstance(p.role, SheriffRoleCard) for p in gm.players if p.is_alive()
        )
