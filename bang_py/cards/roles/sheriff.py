"""Sheriff role from the base game; wins by eliminating all Outlaws and the Renegade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseRole

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ...game_manager_protocol import GameManagerProtocol
    from ...player import Player


class SheriffRoleCard(BaseRole):
    """Role card representing the Sheriff."""

    card_name = "Sheriff"
    victory_message = "Sheriff and Deputies win!"

    def check_win(self, gm: GameManagerProtocol, player: Player) -> bool:
        from .outlaw import OutlawRoleCard
        from .renegade import RenegadeRoleCard

        alive = [p for p in gm.players if p.is_alive()]
        outlaws = any(isinstance(p.role, OutlawRoleCard) for p in alive)
        renegades = any(isinstance(p.role, RenegadeRoleCard) for p in alive)
        return not outlaws and not renegades
