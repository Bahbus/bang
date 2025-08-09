"""Abstract base class for Bang characters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol
    from ..player import Player


class BaseCharacter(ABC):
    """Abstract base class for all Bang characters."""

    # The following attributes are accessed by the game engine and UI to
    # display character information and apply passive modifiers. They are not
    # referenced within this module directly, which may lead Vulture to mark
    # them as unused.
    name: str = "Character"
    description: str = ""
    range_modifier: int = 0
    distance_modifier: int = 0
    starting_health: int = 4

    @abstractmethod
    def ability(self, gm: "GameManagerProtocol", player: "Player", **_: object) -> bool:
        """Perform the character's special ability."""
        # ``**_`` allows subclasses to declare additional keyword arguments
        # without breaking this abstract method's signature.
        raise NotImplementedError
