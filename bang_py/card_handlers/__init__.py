"""Card play dispatch and handler utilities assembled via registry."""

from __future__ import annotations

from importlib import import_module

MODULE_REGISTRY = {
    "dispatch": "bang_py.card_handlers.dispatch",
    "bang": "bang_py.card_handlers.bang_handlers",
}

_modules = {name: import_module(path) for name, path in MODULE_REGISTRY.items()}

register_handler_groups = _modules["dispatch"].register_handler_groups


class CardHandlersMixin(
    _modules["dispatch"].DispatchMixin,
    _modules["bang"].BangHandlersMixin,
):
    """Mixin implementing card play dispatch for ``GameManager``."""


__all__ = ["CardHandlersMixin", "register_handler_groups", "MODULE_REGISTRY"]

