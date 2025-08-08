"""Card play dispatch and handler utilities assembled via registry."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

MODULE_REGISTRY = {
    "dispatch": "bang_py.card_handlers.dispatch",
    "bang": "bang_py.card_handlers.bang_handlers",
}

if TYPE_CHECKING:
    from .dispatch import DispatchMixin, register_handler_groups  # pragma: no cover
    from .bang_handlers import BangHandlersMixin  # pragma: no cover
else:  # pragma: no cover - dynamic import for runtime flexibility
    _modules = {name: import_module(path) for name, path in MODULE_REGISTRY.items()}
    register_handler_groups = _modules["dispatch"].register_handler_groups
    DispatchMixin = _modules["dispatch"].DispatchMixin
    BangHandlersMixin = _modules["bang"].BangHandlersMixin


class CardHandlersMixin(DispatchMixin, BangHandlersMixin):
    """Mixin implementing card play dispatch for ``GameManager``."""


__all__ = ["CardHandlersMixin", "register_handler_groups", "MODULE_REGISTRY"]
