"""Stagecoach card from the base game. Draw two cards."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..deck import Deck
    from ..game_manager_protocol import GameManagerProtocol


class StagecoachCard(BaseCard):
    card_name = "Stagecoach"
    card_type = "action"
    card_set = "base"
    description = "Draw two cards."

    @override
    def play(
        self,
        target: Player | None,
        game: GameManagerProtocol | None = None,
        deck: Deck | None = None,
        **kwargs: Any,
    ) -> None:
        if not target:
            return
        if game:
            game.draw_card(target, 2)
        elif deck:
            for _ in range(2):
                card = deck.draw()
                if card:
                    target.hand.append(card)
