"""Brawl card from the Dodge City expansion. Discard a card to make all others discard one."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:  # pragma: no cover - for type hints only
    from ..game_manager_protocol import GameManagerProtocol

from ..helpers import handle_out_of_turn_discard


class BrawlCard(BaseCard):
    """Discard another card to make everyone discard one."""

    card_name = "Brawl"
    card_type = "action"
    card_set = "dodge_city"
    description = "Discard a card to make all others discard one."

    @override
    def play(
        self,
        target: Player | None = None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        *,
        discard_idx: int = 0,
        victim_indices: dict[int, int] | None = None,
        **kwargs: Any,
    ) -> None:
        if not player or not game or not player.hand:
            return
        if 0 <= discard_idx < len(player.hand):
            cost = player.hand.pop(discard_idx)
        else:
            cost = player.hand.pop(0)
        game.discard_pile.append(cost)
        handle_out_of_turn_discard(game, player, cost)
        victim_indices = victim_indices or {}
        for i, p in enumerate(game.players):
            if p is player:
                continue
            if p.hand:
                idx = victim_indices.get(i, 0)
                if not 0 <= idx < len(p.hand):
                    idx = 0
                card = p.hand.pop(idx)
                game.discard_pile.append(card)
                handle_out_of_turn_discard(game, p, card)
