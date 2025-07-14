from __future__ import annotations

from .card import BaseCard
from ..player import Player
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from ..game_manager import GameManager


class GeneralStoreCard(BaseCard):
    card_name = "General Store"
    card_type = "action"
    card_set = "base"
    description = "Reveal cards for all players to choose one in turn order."

    def play(
        self,
        target: Player,
        player: Player | None = None,
        game: GameManager | None = None,
        choices: List[int] | None = None,
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
