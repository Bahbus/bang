from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager import GameManager
    from ..player import Player


class BaseCharacter(ABC):
    """Abstract base class for all Bang characters."""

    name: str = "Character"
    description: str = ""
    range_modifier: int = 0
    distance_modifier: int = 0
    starting_health: int = 4

    @abstractmethod
    def ability(self, gm: "GameManager", player: "Player", **_: object) -> bool:
        """Perform the character's special ability."""
        raise NotImplementedError

