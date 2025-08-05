"""Deputy role from the base game; wins with the Sheriff when all enemies are gone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseRole

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ...game_manager import GameManager
    from ...player import Player


class DeputyRoleCard(BaseRole):
    """Role card representing a Deputy."""

    card_name = "Deputy"
    victory_message = "Sheriff and Deputies win!"

    def check_win(self, gm: GameManager, player: Player) -> bool:
        from .outlaw import OutlawRoleCard
        from .renegade import RenegadeRoleCard

        alive = [p for p in gm.players if p.is_alive()]
        outlaws = any(isinstance(p.role, OutlawRoleCard) for p in alive)
        renegades = any(isinstance(p.role, RenegadeRoleCard) for p in alive)
        return not outlaws and not renegades
