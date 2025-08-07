"""Bang card game modules."""

from importlib import import_module
from typing import Any

__all__ = [
    "ability_dispatch",
    "card_handlers",
    "cards",
    "characters",
    "deck",
    "deck_factory",
    "deck_manager",
    "events",
    "game_manager",
    "general_store",
    "helpers",
    "network",
    "player",
    "turn_phases",
    "ui",
]


def __getattr__(name: str) -> Any:
    """Dynamically import ``bang_py`` submodules on first access.

    Parameters
    ----------
    name:
        Name of the submodule to import.

    Returns
    -------
    ModuleType
        The requested submodule.

    Raises
    ------
    AttributeError
        If the submodule does not exist.
    """

    try:
        return import_module(f"bang_py.{name}")
    except ModuleNotFoundError as exc:  # pragma: no cover - defensive
        raise AttributeError(f"module 'bang_py' has no attribute {name!r}") from exc
