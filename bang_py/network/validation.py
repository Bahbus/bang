"""Network validation helpers.

This module exposes utility functions used across the networking layer without
pulling in the heavier server dependencies. Keeping validation separate allows
modules such as the UI to reuse the logic without requiring the websockets
package to be installed.
"""

from __future__ import annotations


def validate_player_name(name: str) -> bool:
    """Return ``True`` if ``name`` is a valid player name.

    A valid name is a non-empty printable string no longer than 20 characters.
    """

    if not isinstance(name, str):
        return False
    name = name.strip()
    return bool(name) and len(name) <= 20 and name.isprintable()


__all__ = ["validate_player_name"]
