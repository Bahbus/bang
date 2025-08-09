"""Bible card from the Dodge City expansion. Play as Missed! and then draw one card."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class BibleCard(BaseCard):
    """Missed! effect that also lets the player draw a card."""

    card_name = "Bible"
    card_type = "green"
    card_set = "dodge_city"
    description = "Play as Missed! and then draw one card."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        if not target:
            return
        target.metadata.dodged = True
        if game:
            game.draw_card(player or target)
