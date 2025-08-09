"""Utilities and helpers for optional event deck expansions.

This package bundles the modules that build event decks, dispatch event hooks,
and apply expansion-specific logic during play. The modules are re-exported for
convenient access via :mod:`bang_py.events`.
"""

from __future__ import annotations

from . import event_decks, event_hooks, event_logic

__all__ = ["event_decks", "event_hooks", "event_logic"]
