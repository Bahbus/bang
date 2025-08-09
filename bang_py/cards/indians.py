"""Indians! card from the base game. Others discard Bang! or suffer 1 damage."""

from __future__ import annotations
from .card import BaseCard
from ..player import Player
from ..helpers import handle_out_of_turn_discard
from typing import Any, TYPE_CHECKING, override

if TYPE_CHECKING:
    from ..game_manager_protocol import GameManagerProtocol


class IndiansCard(BaseCard):
    card_name = "Indians!"
    card_type = "action"
    card_set = "base"
    description = "Others discard Bang! or suffer 1 damage."

    @override
    def play(
        self,
        target: Player | None,
        player: Player | None = None,
        game: GameManagerProtocol | None = None,
        **kwargs: Any,
    ) -> None:
        if not game or not player:
            return
        from .bang import BangCard

        for p in game.players:
            if p is player:
                continue
            bang = next((c for c in p.hand if isinstance(c, BangCard)), None)
            if bang:
                p.hand.remove(bang)
                game.discard_pile.append(bang)
                handle_out_of_turn_discard(game, p, bang)
            else:
                before = p.health
                p.take_damage(1)
                if p.health < before:
                    game.on_player_damaged(p, player)
