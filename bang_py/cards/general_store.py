"""General Store card from the base game. Reveal cards for all players to choose one in turn
order."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class GeneralStoreCard(BaseCard):
    card_name = "General Store"
    card_type = "action"
    card_set = "base"
    description = "Reveal cards for all players to choose one in turn order."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        choices: list[int] | None = None,
        **kwargs: Any,
    ) -> None:
        """Reveal cards equal to players and let each choose in order."""
        if not game or not player:
            return

        game.start_general_store(player)
        order = game.general_store_order or []
        selections = choices or []
        for i, p in enumerate(order):
            if game.general_store_cards is None:
                break
            idx = selections[i] if i < len(selections) else 0
            game.general_store_pick(p, idx)
