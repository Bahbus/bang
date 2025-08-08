"""Missed! card from the base game. Negates one Bang! targeting you."""

from __future__ import annotations

try:
    from typing import override
except ImportError:  # pragma: no cover - fallback for Python <3.12
    from typing_extensions import override

from .card import BaseCard
from ..player import Player


class MissedCard(BaseCard):
    card_name = "Missed!"
    card_type = "action"
    card_set = "base"
    description = "Negates one Bang! targeting you."

    @override
    def play(self, target: Player | None, **kwargs) -> None:
        if not target:
            return
        target.metadata.dodged = True
