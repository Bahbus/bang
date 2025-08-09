"""Pony Express card from the Fistful of Cards expansion. Draw three cards."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class PonyExpressCard(BaseCard):
    """Draw three cards."""

    card_name = "Pony Express"
    card_type = "green"
    card_set = "fistful_of_cards"
    description = "Draw three cards."

    @override
    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        if player and game:
            game.draw_card(player, 3)
