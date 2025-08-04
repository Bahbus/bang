"""Tests for card handler module boundaries and registry loading."""

from __future__ import annotations

import sys

from bang_py.card_handlers import MODULE_REGISTRY, CardHandlersMixin


def test_module_registry_loaded() -> None:
    """Ensure modules declared in the registry are imported."""
    for path in MODULE_REGISTRY.values():
        assert path in sys.modules


def test_dispatch_mixin_has_core_dispatch() -> None:
    """Dispatch mixin should provide the core dispatch method."""
    from bang_py.card_handlers.dispatch import DispatchMixin

    assert hasattr(DispatchMixin, "_dispatch_play")


def test_bang_mixin_has_bang_logic() -> None:
    """Bang mixin should expose Bang!-specific helpers."""
    from bang_py.card_handlers.bang_handlers import BangHandlersMixin

    assert hasattr(BangHandlersMixin, "_play_bang_card")


def test_combined_mixin_includes_all_methods() -> None:
    """CardHandlersMixin should combine methods from submixins."""
    assert hasattr(CardHandlersMixin, "_dispatch_play")
    assert hasattr(CardHandlersMixin, "_play_bang_card")

