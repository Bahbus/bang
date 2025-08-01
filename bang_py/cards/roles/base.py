from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ...game_manager import GameManager
    from ...player import Player


class BaseRole(ABC):
    """Base class for all role cards."""

    card_name: str = "Role"
    card_type: str = "role"
    victory_message: str = ""

    @abstractmethod
    def check_win(self, gm: GameManager, player: Player) -> bool:
        """Return ``True`` if this role's winning condition is met."""
        raise NotImplementedError
