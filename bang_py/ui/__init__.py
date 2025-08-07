"""User interface package for the Bang card game.

Provides Qt Quick-based components and utilities for running the game's
interactive client.

See AGENTS.md for UI coding guidelines.
"""

from __future__ import annotations

from .main import BangUI, main

__all__ = ["BangUI", "main"]
